import phonenumbers

def formatar_telefone(numero_bruto: str) -> str:
    try:
        numero = phonenumbers.parse(numero_bruto, "BR")
        if phonenumbers.is_valid_number(numero):
            return phonenumbers.format_number(numero, phonenumbers.PhoneNumberFormat.E164)
        else:
            return "Número inválido"
    except phonenumbers.NumberParseException:
        return "Formato incorreto"

# Teste do formato
print(formatar_telefone("11999998888"))  # Esperado: +5511999998888
