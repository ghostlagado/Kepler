"""Catálogo de departamentos e seus códigos DCO (herdado de legacy/hxh.py).

Cada departamento tem um `meta_group`: o nome exato usado na coluna
"Grupo Operações" da planilha de metas — que nem sempre coincide com o
rótulo exibido (ex.: "Perfumaria" alimenta Beleza, "Eletrônicos" alimenta
Tecnologia, "Infanto-Juvenil" alimenta Infantil).
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class Department:
    key: str  # identificador estável (usado em JSON/histórico)
    label: str  # nome exibido na interface
    meta_group: str  # nome do grupo na planilha de metas
    dco_codes: tuple[str, ...]  # prefixos de DCO que somam neste departamento


DEPARTMENTS: tuple[Department, ...] = (
    Department(
        "beleza", "Beleza", "Perfumaria",
        ("280-", "281-", "282-", "283-", "284-", "285-", "289-"),
    ),
    Department(
        "calcados", "Calçados", "Calçados",
        ("500-", "505-", "510-", "515-", "520-", "540-", "570-", "595-"),
    ),
    Department(
        "tecnologia", "Tecnologia", "Eletrônicos",
        ("530-E", "531-", "532-", "533-", "551-", "552-"),
    ),
    Department(
        "feminino", "Feminino", "Feminino",
        ("180-", "200-", "204-", "205-", "206-", "208-", "210-", "215-",
         "216-", "217-", "220-", "225-", "226-", "227-", "230-", "235-",
         "240-", "245-", "250-", "255-", "260-", "261-", "265-", "270-",
         "275-", "290-", "295-", "296-"),
    ),
    Department(
        "infantil", "Infantil", "Infanto-Juvenil",
        ("100-", "101-", "102-", "105-", "106-", "110-", "115-", "120-",
         "125-", "130-", "131-", "135-", "142-", "145-", "148-", "150-",
         "151-", "165-", "175-", "195-", "196-"),
    ),
    Department(
        "masculino", "Masculino", "Masculino",
        ("300-", "301-", "305-", "306-", "310-", "314-", "315-", "320-",
         "325-", "330-", "331-", "340-", "350-", "360-", "365-", "370-",
         "375-", "380-", "390-", "395-"),
    ),
    Department(
        "moda_casa", "Moda Casa", "Moda Casa",
        ("400-", "405-", "410-", "415-", "420-", "425-", "430-", "435-",
         "440-", "445-"),
    ),
    Department(
        "oculos_biju", "Óculos e Bijuterias", "Óculos e Bijuteria",
        ("560-", "565-"),
    ),
    Department(
        "basket", "Basket", "Basket",
        ("572-",),
    ),
    Department(
        "relogios", "Relógios", "Relógios",
        ("550-",),
    ),
)

# Índice plano de todos os prefixos DCO (o parser busca por presença de
# substring na linha) e mapa chave->Departamento para (de)serialização.
ALL_DCO_CODES: tuple[str, ...] = tuple(
    code for dept in DEPARTMENTS for code in dept.dco_codes
)

DEPARTMENTS_BY_KEY = {dept.key: dept for dept in DEPARTMENTS}
