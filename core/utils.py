import uuid


def gen_uuid() -> str:
    """Gera um UUID v4 como string para uso como chave primária."""
    return str(uuid.uuid4())
