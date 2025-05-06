[2025-05-06  16:36:11  +0000]  [83]  [INFO]  Usando  trabalhador:  uvicorn.workers.UvicornWorker
[2025-05-06  16:36:11  +0000]  [84]  [INFO]  Inicializando  o trabalhador  com  pid:  84
[2025-05-06  16:36:11  +0000]  [85]  [INFO]  Inicializando  o trabalhador  com  pid:  85
[2025-05-06  16:36:11  +0000]  [84]  [INFO] Processo do servidor  iniciado [84]   
[2025-05-06  16:36:11  +0000]  [84]  [INFO]  Aguardando  inicialização  do aplicativo  .
[2025-05-06  16:36:11  +0000]  [84]  [INFO] Inicialização  do aplicativo concluída.  
[2025-05-06  16:36:11  +0000]  [85]  [INFO] Processo do servidor  iniciado [85]   
[2025-05-06  16:36:11  +0000]  [85]  [INFO]  Aguardando  inicialização  do aplicativo  .
[2025-05-06  16:36:11  +0000]  [85]  [INFO] Inicialização  do aplicativo concluída.  
127.0.0.1:60408  -  "CABEÇA  /  HTTP/1.1"  404
==>  Seu  serviço  está  ativo  🎉
35.197.37.4:0  -  "OBTER  /  HTTP/1.1"  404
INFO:draana:📩  Payload  recebido:  {'update_id':  530007346,  'message':  {'message_id':  10,  'from':  {'id':  6601584721,  'is_bot':  False,  'first_name':  'Andre',  'last_name':  'Luis',  'language_code':  'pt-br'},  'chat':  {'id':  6601584721,  'first_name':  'Andre',  'last_name':  'Luis',  'type':  'private'},  'date':  1746549402,  'text':  'ola'}}
INFO:draana.telegram_utils:📝  processar_mensagem  -  chat_id=6601584721,  texto='ola'
INFO:draana.telegram_utils:🤖  Resposta  do  modelo:  '**Oi,  querida!**  💛  Vamos  começar  do  zero  com  todo  cuidado!  
👉  **Me  conta  seu  nome  e  idade  pra  eu  te  orientar  direitinho,  tá?**  (Isso  faz  TODA  diferença  pra  entender  seus  sintomas!)  
###  🎯  **Enquanto  isso,  já  adianto:**  
-  Se  você tiver  **calorões,  insônia  ou  proteção**,  pode  ser  **hormonal**  (e  tem  solução!)  
-  Se  tá  se  sentindo  **esgotada  sem  motivo**,  seu  **cortisol**  pode  estar  gritando  por  ajuda  
-  **Nada  aqui  é  "só  estresse"**  –  seu  corpo  merece  atenção!  
**Eu  falo:**  
❓  **Qual  seu  maior  incômodo  hoje?**  
❓  **Algum  médico  já  disse  que  "é  normal"  sem  te  examinar  direito?**  *(compartilha  comigo  essa  história!)*  
*(Tô  aqui  pra  te  ouvir  SEM  julgamentos!)*  ✨  
**Ah!**  Se  preferir,  pode  me  chamar  de  **Dra.  Ana**  –  fico  à  vontade!  😊'
INFO:draana.telegram_utils:📤  Enviando  mensagem  -  URL: https://api.telegram.org/bot7843033047:AAFHT2v4c2d5-gJcscqVcDswsoMNUNeAyHo 
/sendMessage,  payload:  {'chat_id':  6601584721,  'text':  '**Oi,  querida!**  💛  Vamos  começar  do  zero  com  todo  cuidado!   \n\n👉  **Me  conta  seu  nome  e  idade  pra  eu  te  orientar  direitinho,  tá?**  (Isso  faz  TODA  diferença  pra  entender  seus  sintomas!)   \n\n###  🎯  **Enquanto  isso,  já  adianto:**   \n-  Se  tiver  **calorões,  insônia  ou  benéfica**,  pode  ser  **hormonal**  (e  tem  solução!)   \n-  Se  tá  se  tá sentindo  **esgotada  sem  **,  seu  **cortisol**  pode  estar  gritando  por  ajuda   \n-  **Nada  aqui  é  "só  estresse"**  –  seu  corpo  merece  atenção!   \n\n**Me  fala:**   \n❓  **Qual  seu  maior  incômodo  hoje?**   \n❓  **Algum  médico  já  disse  que  "é  normal"  sem  te  examinar  direito?**  *(compartilha  comigo  essa  história!)*   \n\n*(Tô  aqui  pra  te  ouvir  SEM  julgamentos!)*  ✨   \n\n**Ah!**  Se  preferir,  pode  me  chamar  de  **Dra.  Ana**  –  fico  à  vontade!  😊'}
INFO:draana.telegram_utils:📥  Telegram  respondeu:  404  -  {"ok":false,"error_code":404,"description":"Não  encontrado"}
INFO:draana:✅  Mensagem  processada  para  usuário  6601584721
91.108.5.6:0  -  "POST  /webhook  HTTP/1.1"  200