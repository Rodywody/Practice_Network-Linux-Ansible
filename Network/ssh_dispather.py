"""Controls selection of proper class based on the device type."""
from typing import Any, Type, Optional
from typing import TYPE_CHECKING
import re
from netmiko.exceptions import ConnectionException
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException
from netmiko.a10 import A10SSH
from netmiko.accedian import AccedianSSH
from netmiko.adtran import AdtranOSSSH, AdtranOSTelnet
from netmiko.adva import AdvaAosFsp150F3SSH, AdvaAosFsp150F2SSH
from netmiko.alcatel import AlcatelAosSSH
from netmiko.allied_telesis import AlliedTelesisAwplusSSH
from netmiko.arista import AristaSSH, AristaTelnet
from netmiko.arista import AristaFileTransfer
from netmiko.arris import ArrisCERSSH
from netmiko.apresia import ApresiaAeosSSH, ApresiaAeosTelnet
from netmiko.aruba import ArubaSSH
from netmiko.audiocode import (
    Audiocode72SSH,
    Audiocode66SSH,
    AudiocodeShellSSH,
    Audiocode72Telnet,
    Audiocode66Telnet,
    AudiocodeShellTelnet,
)
from netmiko.brocade import BrocadeFOSSSH
from netmiko.broadcom import BroadcomIcosSSH
from netmiko.calix import CalixB6SSH, CalixB6Telnet
from netmiko.casa import CasaCMTSSSH
from netmiko.cdot import CdotCrosSSH
from netmiko.centec import CentecOSSSH, CentecOSTelnet
from netmiko.checkpoint import CheckPointGaiaSSH
from netmiko.ciena import CienaSaosSSH, CienaSaosTelnet, CienaSaosFileTransfer
from netmiko.cisco import CiscoAsaSSH, CiscoAsaFileTransfer
from netmiko.cisco import CiscoFtdSSH
from netmiko.cisco import (
    CiscoIosSSH,
    CiscoIosFileTransfer,
    CiscoIosTelnet,
    CiscoIosSerial,
)
from netmiko.cisco import CiscoNxosSSH, CiscoNxosFileTransfer
from netmiko.cisco import CiscoS200SSH, CiscoS200Telnet
from netmiko.cisco import CiscoS300SSH, CiscoS300Telnet
from netmiko.cisco import CiscoTpTcCeSSH
from netmiko.cisco import CiscoViptelaSSH
from netmiko.cisco import CiscoWlcSSH
from netmiko.cisco import CiscoXrSSH, CiscoXrTelnet, CiscoXrFileTransfer
from netmiko.citrix import NetscalerSSH
from netmiko.cloudgenix import CloudGenixIonSSH
from netmiko.coriant import CoriantSSH
from netmiko.dell import DellDNOS6SSH
from netmiko.dell import DellDNOS6Telnet
from netmiko.dell import DellForce10SSH
from netmiko.dell import DellOS10SSH, DellOS10FileTransfer
from netmiko.dell import DellSonicSSH
from netmiko.dell import DellPowerConnectSSH
from netmiko.dell import DellPowerConnectTelnet
from netmiko.dell import DellIsilonSSH
from netmiko.digi import DigiTransportSSH
from netmiko.dlink import DlinkDSTelnet, DlinkDSSSH
from netmiko.eltex import EltexSSH, EltexEsrSSH
from netmiko.endace import EndaceSSH
from netmiko.enterasys import EnterasysSSH
from netmiko.ericsson import (
    EricssonIposSSH,
    EricssonMinilink63SSH,
    EricssonMinilink66SSH,
)
from netmiko.extreme import ExtremeErsSSH
from netmiko.extreme import ExtremeExosSSH, ExtremeExosFileTransfer
from netmiko.extreme import ExtremeExosTelnet
from netmiko.extreme import ExtremeNetironSSH
from netmiko.extreme import ExtremeNetironTelnet
from netmiko.extreme import ExtremeNosSSH
    if device_type not in platforms:
        if device_type is None:
            msg_str = platforms_str
        else:
            msg_str = telnet_platforms_str if "telnet" in device_type else platforms_str
        raise ValueError(
            "Unsupported 'device_type' "
            "currently supported platforms are: {}".format(msg_str)
        )
    ConnectionClass = ssh_dispatcher(device_type)
    return ConnectionClass(*args, **kwargs)


def TelnetFallback(*args: Any, **kwargs: Any) -> "BaseConnection":
    """If an SSH connection fails, try to fallback to Telnet."""
    try:
        return ConnectHandler(*args, **kwargs)
    except (NetmikoTimeoutException, ConnectionRefusedError):
        device_type = kwargs["device_type"]
        # platforms_str is the base form (i.e. does not have the '_ssh' suffix)
        if device_type in platforms_str:
            alternative_device = f"{device_type}_telnet"
        elif "_ssh" in device_type:
            alternative_device = re.sub("_ssh", "_telnet", device_type)

        if alternative_device in platforms:
            kwargs["device_type"] = alternative_device
            return ConnectHandler(*args, **kwargs)
        raise


def ConnLogOnly(
    log_file: str = "netmiko.log",
    log_level: Optional[int] = None,
    log_format: Optional[str] = None,
    **kwargs: Any,
) -> Optional["BaseConnection"]:
    """
    Dispatcher function that will return either: netmiko_object or None

    Excluding errors in logging configuration should never generate an exception
    all errors should be logged.
    """

    import logging

    if log_level is None:
        log_level = logging.ERROR
    if log_format is None:
        log_format = "%(asctime)s %(levelname)s %(name)s %(message)s"

    logging.basicConfig(filename=log_file, level=log_level, format=log_format)
    logger = logging.getLogger(__name__)

    try:
        kwargs["auto_connect"] = False
        net_connect = ConnectHandler(**kwargs)
        hostname = net_connect.host
        port = net_connect.port
        device_type = net_connect.device_type

        net_connect._open()
        msg = f"Netmiko connection succesful to {hostname}:{port}"
        logger.info(msg)
        return net_connect
    except NetmikoAuthenticationException as e:
        msg = (
            f"Authentication failure to: {hostname}:{port} ({device_type})\n\n{str(e)}"
        )
        logger.error(msg)
        return None
    except NetmikoTimeoutException as e:
        if "DNS failure" in str(e):
            msg = f"Device failed due to a DNS failure, hostname {hostname}"
        elif "TCP connection to device failed" in str(e):
            msg = f"Netmiko was unable to reach the provided host and port: {hostname}:{port}"
            msg += f"\n\n{str(e)}"
        else:
            msg = f"An unknown NetmikoTimeoutException occurred:\n\n{str(e)}"
        logger.error(msg)
        return None
    except Exception as e:
        msg = f"An unknown exception occurred during connection:\n\n{str(e)}"
        logger.error(msg)
        return None


def ConnUnify(
    **kwargs: Any,
) -> "BaseConnection":
    try:
        kwargs["auto_connect"] = False
        net_connect = ConnectHandler(**kwargs)
        hostname = net_connect.host
        port = net_connect.port
        device_type = net_connect.device_type
        general_msg = f"Connection failure to {hostname}:{port} ({device_type})\n\n"

        net_connect._open()
        return net_connect
    except NetmikoAuthenticationException as e:
        msg = general_msg + str(e)
        raise ConnectionException(msg)
    except NetmikoTimeoutException as e:
        msg = general_msg + str(e)
        raise ConnectionException(msg)
    except Exception as e:
        msg = f"An unknown exception occurred during connection:\n\n{str(e)}"
        raise ConnectionException(msg)


def ssh_dispatcher(device_type: str) -> Type["BaseConnection"]:
    """Select the class to be instantiated based on vendor/platform."""
    return CLASS_MAPPER[device_type]


def redispatch(
    obj: "BaseConnection", device_type: str, session_prep: bool = True
) -> None:
    """Dynamically change Netmiko object's class to proper class.
    Generally used with terminal_server device_type when you need to redispatch after interacting
    with terminal server.
    """
    new_class = ssh_dispatcher(device_type)
    obj.device_type = device_type
    obj.__class__ = new_class
    if session_prep:
        obj._try_session_preparation()


def FileTransfer(*args: Any, **kwargs: Any) -> "BaseFileTransfer":
    """Factory function selects the proper SCP class and creates object based on device_type."""
    if len(args) >= 1:
        device_type = args[0].device_type
    else:
        device_type = kwargs["ssh_conn"].device_type
    if device_type not in scp_platforms:
        raise ValueError(
            "Unsupported SCP device_type: "
            "currently supported platforms are: {}".format(scp_platforms_str)
        )
    FileTransferClass: Type["BaseFileTransfer"]
    FileTransferClass = FILE_TRANSFER_MAP[device_type]
    return FileTransferClass(*args, **kwargs)
