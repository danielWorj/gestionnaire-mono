"""
licensing.hardware_id
======================

Détermine un identifiant matériel (HWID) stable pour la machine locale,
basé sur son adresse MAC. Cet identifiant est celui qui doit être inclus
(champ "hwid") dans chaque licence signée par l'administrateur, et c'est
celui que license_manager compare à la licence installée.

`uuid.getnode()` est le moyen standard le plus simple, mais sur certaines
machines (pas de carte réseau physique détectée, VM, conteneur...) Python
peut se rabattre sur un identifiant 48 bits généré aléatoirement plutôt
que de renvoyer une vraie adresse MAC. Dans ce cas, on retente via psutil
en ciblant explicitement une interface réseau physique.
"""

import re
import uuid

_HEX_CHARS_RE = re.compile(r'[^0-9a-fA-F]')

# Interfaces à ignorer quand on cherche une carte réseau "physique" :
# boucle locale, interfaces virtuelles, VPN, etc.
_IGNORED_INTERFACE_PREFIXES = ('lo', 'docker', 'veth', 'br-', 'vmnet', 'vboxnet', 'tun', 'tap', 'utun')


def _normalize_mac(raw: str) -> str:
    """Normalise une adresse MAC vers un format hexadécimal minuscule, sans séparateurs.

    Exemple : '00:1A:2B:3C:4D:5E' -> '001a2b3c4d5e'
    """
    return _HEX_CHARS_RE.sub('', raw).lower()


def _is_locally_administered_or_random(node: int) -> bool:
    """
    Détecte si l'ID renvoyé par uuid.getnode() est probablement une valeur
    générée aléatoirement (et non une vraie adresse MAC). D'après la RFC 4122,
    uuid.getnode() active le bit multicast (bit de poids faible du premier
    octet) quand il génère un ID de repli.
    """
    first_octet = (node >> 40) & 0xFF
    return bool(first_octet & 0x01)


def _get_mac_via_psutil(interface: str = None):
    """Cherche une adresse MAC via psutil, en ciblant une interface précise
    si demandé, sinon en prenant la première interface physique plausible."""
    try:
        import psutil
    except ImportError:
        return None

    interfaces = psutil.net_if_addrs()

    def _extract_mac(addr_list):
        for addr in addr_list:
            family_name = getattr(addr.family, 'name', str(addr.family))
            if family_name in ('AF_LINK', 'AF_PACKET') and addr.address:
                if addr.address not in ('00:00:00:00:00:00', ''):
                    return addr.address
        return None

    if interface:
        addr_list = interfaces.get(interface)
        return _extract_mac(addr_list) if addr_list else None

    for name, addr_list in interfaces.items():
        lname = name.lower()
        if lname.startswith(_IGNORED_INTERFACE_PREFIXES):
            continue
        mac = _extract_mac(addr_list)
        if mac:
            return mac

    return None


def get_hwid(interface: str = None) -> str:
    """
    Renvoie l'identifiant matériel (HWID) de la machine locale : une adresse
    MAC normalisée en hexadécimal minuscule sans séparateurs (ex: '001a2b3c4d5e').

    Args:
        interface: nom optionnel d'une interface réseau précise à cibler
            (ex: 'eth0', 'Ethernet'). Utile quand la machine a plusieurs
            cartes réseau et qu'on veut fixer la licence sur une carte en
            particulier. Si absent, on utilise uuid.getnode(), avec repli
            sur psutil si le résultat semble aléatoire.

    Note: cette fonction DOIT produire exactement le même résultat que celui
    utilisé côté admin au moment de signer la licence (même méthode, même
    interface le cas échéant), sans quoi la vérification hwid échouera
    systématiquement.
    """
    if interface:
        mac = _get_mac_via_psutil(interface)
        if mac:
            return _normalize_mac(mac)
        # Si l'interface demandée est introuvable via psutil, on retombe
        # sur le comportement par défaut plutôt que d'échouer silencieusement.

    node = uuid.getnode()

    if _is_locally_administered_or_random(node):
        mac = _get_mac_via_psutil()
        if mac:
            return _normalize_mac(mac)
        # Aucune carte physique trouvable : on garde quand même la valeur
        # de uuid.getnode(), qui reste stable d'un lancement à l'autre sur
        # une même machine (elle est mise en cache par le système).

    return f'{node:012x}'