# 1. Importações necessárias
import os
import logging
import psycopg2 # Biblioteca para interagir com PostgreSQL
import requests # Biblioteca para fazer requisições HTTP (para OpenRouter)
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from datetime import datetime
# Para carregar variáveis de ambiente de um arquivo .env (opcional, mas recomendado para testes locais)
# Se for usar, instale com: pip install python-dotenv
try:
    from dotenv import load_dotenv
    load_dotenv() # Carrega variáveis do arquivo .env, se existir
    print("Variáveis de ambiente do .env carregadas (se o arquivo existir).")
except ImportError:
    print("Biblioteca python-dotenv não encontrada. Carregando variáveis do ambiente do sistema.")
    pass

# 2. Configuração
# Carregue estas variáveis a partir do ambiente (Render ou .env)
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENROUTER_API_KEY = os.environ.get('OPENROUTER_API_KEY')
# Esta é a 'Internal Connection String' ou 'External Connection String' do seu BD no Render
DATABASE_URL = os.environ.get('DATABASE_URL')
# Escolha o modelo que você quer usar no OpenRouter
# Exemplo: "openai/gpt-3.5-turbo", "google/gemini-flash-1.5", "anthropic/claude-3-haiku"
OPENROUTER_MODEL = os.environ.get('OPENROUTER_MODEL', "openai/gpt-3.5-turbo")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"
# Quantas mensagens do histórico enviar para a IA (ajuste conforme necessário)
HISTORY_LIMIT = 20
# ***** NOVO: Definição do System Prompt *****
# Instrução geral para a IA. Pode ser configurada via variável de ambiente.
SYSTEM_PROMPT = os.environ.get(
    'SYSTEM_PROMPT',
    "Você é um assistente de chatbot chamado Parceiro IA. Sua tarefa é ajudar o usuário com programação, respondendo de forma didática e prestativa em português do Brasil. Forneça explicações claras e exemplos de código quando apropriado."
) # Defina seu prompt padrão aqui

# 3. Configuração de Logging (para vermos o que está acontecendo)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Define um logger específico para este módulo
logger = logging.getLogger(__name__)

# 4. Funções do Banco de Dados (Memória do Bot)

def get_db_connection():
    """
    Estabelece e retorna uma conexão com o banco de dados PostgreSQL.
    Retorna None se a conexão falhar.
    """
    if not DATABASE_URL:
        logger.error("DATABASE_URL não está configurada.")
        return None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        # Descomente a linha abaixo para testar a conexão no início
        # logger.info("Conexão com o banco de dados estabelecida com sucesso.")
        return conn
    except Exception as e:
        logger.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def setup_database():
    """
    Garante que a tabela para armazenar o histórico exista no banco de dados.
    Cria a tabela e o índice se eles não existirem.
    """
    conn = get_db_connection()
    if not conn:
        logger.error("Não foi possível conectar ao BD para o setup.")
        return
    try:
        with conn.cursor() as cur:
            # SQL para criar a tabela 'chat_history' se ela não existir
            cur.execute("""
                CREATE TABLE IF NOT EXISTS chat_history (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    user_id BIGINT NOT NULL,
                    message_id BIGINT,
                    role VARCHAR(10) NOT NULL CHECK (role IN ('user', 'assistant')), -- Garante roles válidos
                    content TEXT NOT NULL,
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit() # Commit após criar a tabela
            logger.info("Tabela 'chat_history' verificada/criada.")

            # SQL para criar um índice composto para otimizar a busca do histórico
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_history_chat_id_timestamp
                ON chat_history (chat_id, timestamp DESC);
            """)
            conn.commit() # Commit após criar o índice
            logger.info("Índice 'idx_chat_history_chat_id_timestamp' verificado/criado.")

    except Exception as e:
        logger.error(f"Erro ao configurar a tabela/índice do banco de dados: {e}")
        conn.rollback() # Desfaz alterações em caso de erro
    finally:
        if conn:
            conn.close()
            # logger.info("Conexão com BD fechada após setup.")

def save_message(chat_id, user_id, message_id, role, content):
    """
    Salva uma única mensagem (do usuário ou do bot) no banco de dados.
    """
    # Não salva mensagens vazias
    if not content:
        logger.warning(f"Tentativa de salvar mensagem vazia para chat_id={chat_id}, role={role}. Ignorando.")
        return

    conn = get_db_connection()
    if not conn:
        logger.error(f"Não foi possível salvar mensagem (role={role}, chat_id={chat_id}). Sem conexão com BD.")
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO chat_history (chat_id, user_id, message_id, role, content)
                VALUES (%s, %s, %s, %s, %s)
            """, (chat_id, user_id, message_id, role, content))
            conn.commit()
            # logger.info(f"Mensagem salva: chat_id={chat_id}, role={role}") # Log menos verboso
    except Exception as e:
        logger.error(f"Erro ao salvar mensagem (chat_id={chat_id}, role={role}): {e}")
        conn.rollback()
    finally:
        if conn:
            conn.close()

def get_history(chat_id, limit=HISTORY_LIMIT):
    """
    Recupera as últimas 'limit' mensagens (user/assistant) para um chat específico,
    ordenadas cronologicamente (mais antiga primeiro), prontas para a API.
    """
    conn = get_db_connection()
    history = []
    if not conn:
        logger.error(f"Não foi possível buscar histórico (chat_id={chat_id}). Sem conexão com BD.")
        return history # Retorna lista vazia se não conectar
    try:
        with conn.cursor() as cur:
            # SQL otimizado pelo índice: busca as últimas 'limit' mensagens pelo timestamp DESC
            # e depois reordena por timestamp ASC para manter a ordem cronológica na subquery.
            cur.execute("""
                SELECT role, content FROM (
                    SELECT role, content, timestamp
                    FROM chat_history
                    WHERE chat_id = %s AND role IN ('user', 'assistant') -- Garante pegar só user/assistant
                    ORDER BY timestamp DESC
                    LIMIT %s
                ) AS recent_messages
                ORDER BY timestamp ASC;
            """, (chat_id, limit))
            rows = cur.fetchall()
            # Formata o resultado como a lista de dicionários esperada pela API
            history = [{"role": row[0], "content": row[1]} for row in rows]
            logger.info(f"Histórico recuperado para chat_id={chat_id}: {len(history)} mensagens.")
    except Exception as e:
        logger.error(f"Erro ao recuperar histórico (chat_id={chat_id}): {e}")
    finally:
        if conn:
            conn.close()
    return history

# 5. Função de Interação com a IA (OpenRouter)

def get_ai_response(messages_for_api):
    """
    Envia a lista de mensagens formatada (incluindo system prompt)
    para a API do OpenRouter e retorna a resposta da IA.
    """
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY não está configurada.")
        return "Desculpe, não consigo me conectar à IA no momento (sem chave)."

    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        # Adicionar referências pode ajudar o OpenRouter a identificar seu tráfego
        # "HTTP-Referer": "SEU_SITE_OU_APP_URL", # Opcional
        # "X-Title": "NOME_DO_SEU_BOT", # Opcional
    }
    payload = {
        "model": OPENROUTER_MODEL,
        "messages": messages_for_api,
        # Outros parâmetros opcionais (temperature, max_tokens, etc.) podem ser adicionados aqui
        # "temperature": 0.7,
        # "max_tokens": 1000,
    }

    logger.info(f"Enviando {len(messages_for_api)} mensagens para o modelo {OPENROUTER_MODEL}...")
    # Log do payload (cuidado com dados sensíveis se logar tudo)
    # logger.debug(f"Payload para OpenRouter: {payload}")

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload, timeout=90) # Timeout de 90 segundos
        response.raise_for_status() # Verifica erros HTTP (4xx, 5xx)

        result = response.json()

        # Tratamento de erro mais robusto para a resposta
        if 'choices' not in result or not result['choices']:
            logger.error(f"Resposta da API inesperada (sem 'choices'): {result}")
            return "Desculpe, recebi uma resposta inesperada da IA."
        if 'message' not in result['choices'][0] or 'content' not in result['choices'][0]['message']:
            logger.error(f"Resposta da API inesperada (sem 'message' ou 'content'): {result}")
            return "Desculpe, recebi uma resposta mal formatada da IA."

        ai_content = result['choices'][0]['message']['content']
        logger.info("Resposta da IA recebida com sucesso.")
        return ai_content.strip() if ai_content else "Desculpe, a IA retornou uma resposta vazia."

    except requests.exceptions.Timeout:
        logger.error("Timeout ao chamar a API do OpenRouter.")
        return "Desculpe, a IA demorou muito para responder. Tente novamente mais tarde."
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro na requisição para OpenRouter: {e}")
        error_message = "Desculpe, ocorreu um problema técnico ao tentar falar com a inteligência artificial."
        if e.response is not None:
            logger.error(f"Status da API: {e.response.status_code}")
            try:
                api_error = e.response.json()
                logger.error(f"Erro detalhado da API: {api_error}")
                # Tenta pegar uma mensagem de erro mais específica da API, se disponível
                if 'error' in api_error and 'message' in api_error['error']:
                   error_message += f" (Detalhe: {api_error['error']['message']})"
            except ValueError:
                logger.error(f"Corpo da resposta da API (não JSON): {e.response.text[:500]}...") # Limita o log
        return error_message
    except Exception as e: # Pega outras exceções inesperadas
        logger.exception(f"Erro inesperado ao obter resposta da IA: {e}") # Loga o traceback completo
        return "Desculpe, ocorreu um erro inesperado no processamento da IA."


# 6. Handlers do Telegram (Comandos e Mensagens)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para o comando /start. Envia uma mensagem de boas-vindas.
    """
    user = update.effective_user
    if user:
        await update.message.reply_html(
            rf"Olá, {user.mention_html()}! Eu sou seu assistente com memória. Envie uma mensagem para começarmos.",
        )
        logger.info(f"Usuário {user.id} ({user.username}) iniciou o bot no chat {update.message.chat_id}.")
    else:
         await update.message.reply_text("Olá! Eu sou seu assistente com memória. Envie uma mensagem para começarmos.")
         logger.info(f"Usuário não identificado iniciou o bot no chat {update.message.chat_id}.")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handler para mensagens de texto recebidas (não comandos).
    Processa a mensagem, consulta a IA com histórico e responde.
    """
    # Ignora mensagens que não sejam de texto ou que não venham de um usuário
    if not update.message or not update.message.text or not update.effective_user:
        return

    chat_id = update.message.chat_id
    user_id = update.effective_user.id
    message_id = update.message.message_id
    user_message_content = update.message.text

    logger.info(f"Mensagem recebida: chat_id={chat_id}, user_id={user_id}, msg='{user_message_content[:50]}...'")

    # Etapa 1: Salvar a mensagem do usuário no banco de dados (memória)
    save_message(chat_id, user_id, message_id, 'user', user_message_content)

    # Etapa 2: Recuperar o histórico recente (user/assistant) do banco de dados
    conversation_history_db = get_history(chat_id, limit=HISTORY_LIMIT)

    # Etapa 3: Montar a lista de mensagens para enviar à API
    # Começa SEMPRE com o System Prompt definido globalmente
    messages_for_api = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]
    # Adiciona o histórico recuperado do banco de dados
    messages_for_api.extend(conversation_history_db)

    # Etapa 3.1: Verificação - Adicionar a mensagem atual do usuário se não estiver no histórico recuperado
    # Isso garante que a mensagem mais recente seja processada, especialmente no primeiro turno ou após falha no get_history.
    # Nota: get_history DEVERIA retornar a última mensagem do usuário se save_message funcionou.
    # Esta é uma camada extra de segurança.
    if not conversation_history_db or conversation_history_db[-1].get("role") != "user" or conversation_history_db[-1].get("content") != user_message_content:
         messages_for_api.append({"role": "user", "content": user_message_content})
         # logger.warning(f"Adicionada mensagem atual do usuário explicitamente ao payload da API para chat_id={chat_id}.")


    # Etapa 4: Indicar ao usuário que o bot está processando (feedback visual)
    try:
        await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    except Exception as e:
        logger.warning(f"Não foi possível enviar 'typing' para chat_id={chat_id}: {e}")


    # Etapa 5: Obter a resposta da IA
    ai_response_content = get_ai_response(messages_for_api)


    # Etapa 6: Enviar a resposta da IA de volta ao Telegram
    # Se a resposta da IA não for vazia
    if ai_response_content:
        try:
            sent_message = await update.message.reply_text(ai_response_content)
            bot_message_id = sent_message.message_id # ID da mensagem que o bot enviou

            # Etapa 7: Salvar a resposta da IA no banco de dados (memória)
            # Obtém o ID do bot a partir do contexto
            if hasattr(context.bot, 'id'):
                 bot_id = context.bot.id
                 save_message(chat_id, bot_id, bot_message_id, 'assistant', ai_response_content)
            else:
                 logger.warning(f"Não foi possível obter context.bot.id para salvar resposta do assistant em chat_id={chat_id}")
                 # Salva mesmo sem o user_id do bot (usando 0 ou outro placeholder)
                 save_message(chat_id, 0, bot_message_id, 'assistant', ai_response_content)

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem de resposta ou salvar resposta do bot para chat_id={chat_id}: {e}")
            # Tenta notificar o usuário sobre o erro de envio, se possível
            try:
                 await update.message.reply_text("Desculpe, tive um problema ao tentar enviar a resposta.")
            except Exception as final_e:
                 logger.error(f"Falha até mesmo ao enviar mensagem de erro para chat_id={chat_id}: {final_e}")
    else:
        # Se ai_response_content for None ou vazio (devido a erro na API ou resposta vazia)
        logger.warning(f"Nenhuma resposta da IA para enviar ao usuário no chat_id={chat_id}.")
        # Opcional: Enviar uma mensagem indicando que não houve resposta
        # await update.message.reply_text("Não consegui gerar uma resposta desta vez.")


# 7. Função Principal (main)

def main() -> None:
    """
    Função principal que configura e inicia o bot do Telegram.
    """
    # Verifica se as variáveis de ambiente essenciais foram definidas
    if not TELEGRAM_BOT_TOKEN:
        logger.critical("### ERRO CRÍTICO: Variável de ambiente TELEGRAM_BOT_TOKEN não definida! ###")
        return
    if not OPENROUTER_API_KEY:
        logger.critical("### ERRO CRÍTICO: Variável de ambiente OPENROUTER_API_KEY não definida! ###")
        return
    if not DATABASE_URL:
        logger.critical("### ERRO CRÍTICO: Variável de ambiente DATABASE_URL não definida! ###")
        return

    logger.info(">>> Configurações carregadas <<<")
    logger.info(f"Modelo OpenRouter: {OPENROUTER_MODEL}")
    logger.info(f"Limite de Histórico: {HISTORY_LIMIT}")
    logger.info(f"System Prompt: {SYSTEM_PROMPT[:100]}...") # Log inicial do prompt

    # Garante que a tabela do banco de dados esteja pronta antes de iniciar o bot
    logger.info(">>> Configurando o banco de dados... <<<")
    setup_database()
    logger.info(">>> Banco de dados configurado. <<<")

    logger.info(">>> Iniciando o bot do Telegram... <<<")

    # Cria a aplicação do bot com o token
    try:
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    except Exception as e:
        logger.critical(f"### ERRO CRÍTICO ao criar a aplicação do Telegram: {e} ###")
        logger.critical("Verifique se o TELEGRAM_BOT_TOKEN está correto e válido.")
        return

    # Registra os handlers (comandos e mensagens)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    # Adicionar outros handlers aqui (para fotos, comandos específicos, etc.) se necessário

    # Inicia o bot (fica escutando por novas mensagens)
    logger.info(">>> Bot pronto e escutando por mensagens! <<<")
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES) # Processa todos os tipos de updates
    except Exception as e:
         logger.critical(f"### ERRO CRÍTICO durante a execução do bot (run_polling): {e} ###")
         # Possíveis causas: problema de rede, token inválido/revogado, conflito (outro bot rodando com mesmo token?)


# Ponto de entrada do script: executa a função main
if __name__ == '__main__':
    main()