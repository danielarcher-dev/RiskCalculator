import pytest
# from metrics import calculate_q_metric
import accounts.option_chain as option_chain
from accounts.instrument import Instrument
from schwab import client as SchwabClient
from datetime import datetime

def test_parse_occ_symbol_expiration():
    occ_symbol = "GME   250919P00027000"
    result = Instrument.parse_occ_symbol(occ_symbol)
    assert result["expiration"] == datetime.strptime("250919", '%y%m%d').date()

def test_parse_occ_symbol_strike():
    occ_symbol = "GME   250919P00027000"
    result = Instrument.parse_occ_symbol(occ_symbol)
    assert result["strike"] == float(27)

def test_parse_occ_symbol_put():
    occ_symbol = "GME   250919P00027000"
    result = Instrument.parse_occ_symbol(occ_symbol)
    assert result["option_type"] == SchwabClient.Client.Options.ContractType.PUT

def test_parse_occ_symbol_call():
    occ_symbol = "GME   250919C00027000"
    result = Instrument.parse_occ_symbol(occ_symbol)
    assert result["option_type"] == SchwabClient.Client.Options.ContractType.CALL
