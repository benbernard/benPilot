"""In-memory observations only; no hardware objects or device interfaces.

Does not edit production code, inherited tests, or assertion expectations.
Each invocation starts a new process so platform globals cannot leak in.
"""
import json
import sys
from cffi import FFI
from opendbc.safety.tests.test_chrysler import TestChryslerSafety
from opendbc.safety.tests.common import CANPackerPanda, make_msg
from opendbc.safety.tests.libsafety import libsafety_py

case, dbc = sys.argv[1:]
fixture = TestChryslerSafety()
fixture.setUp()
fixture.packer = CANPackerPanda(dbc)
safety = fixture.safety
observer = FFI()
observer.cdef('extern bool forward_gear; extern bool long_allowed;')
state = observer.dlopen(libsafety_py.libsafety_fn)


def snapshot():
  return {'forward_gear': bool(state.forward_gear), 'long_allowed': bool(state.long_allowed),
          'controls_allowed': bool(safety.get_controls_allowed()),
          'cruise_engaged_prev': bool(safety.get_cruise_engaged_prev())}


result = {'case': case, 'dbc': dbc, 'initial': snapshot()}
if case == 'cruise':
  result['initial_ACC_active_rx_valid'] = bool(fixture._rx(fixture._pcm_status_msg(True)))
  result['ACC_active_without_gear_fixture'] = snapshot()
  # Feed an ordinary simulated forward-gear state using the unmodified DBC.
  result['gear_rx_valid'] = bool(fixture._rx(fixture.packer.make_can_msg_panda('Transmission_Status', 0, {'Gear_State': 4})))
  result['after_gear'] = snapshot()
  result['stationary_ACC_inactive_rx_valid'] = bool(fixture._rx(fixture._pcm_status_msg(False)))
  result['stationary_ACC_inactive'] = snapshot()
  result['speed_rx_valid'] = bool(fixture._rx(fixture._speed_msg(10)))
  result['moving_ACC_inactive_rx_valid'] = bool(fixture._rx(fixture._pcm_status_msg(False)))
  result['moving_ACC_inactive'] = snapshot()
  result['moving_ACC_active_rx_valid'] = bool(fixture._rx(fixture._pcm_status_msg(True)))
  result['moving_ACC_active'] = snapshot()
elif case == 'buttons':
  result['accepted'] = {}
  for enabled in (False, True):
    safety.set_controls_allowed(enabled)
    result['accepted'][str(enabled)] = {
      name: bool(fixture._tx(fixture._button_msg(cancel=cancel, resume=resume)))
      for name, cancel, resume in [('empty', False, False), ('cancel', True, False),
                                   ('resume', False, True), ('combined', True, True)]}
elif case == 'lists':
  result['fixture_TX_messages'] = fixture.TX_MSGS
  result['fixture_camera_blacklist'] = fixture.FWD_BLACKLISTED_ADDRS
  result['heartbeat_camera_forward_destination'] = safety.safety_fwd_hook(2, 0x2d9)
  result['in_memory_zero_payload_TX_accepted'] = {
    'DAS_3': bool(fixture._tx(make_msg(0, 0x1f4, 8))),
    'DAS_5': bool(fixture._tx(make_msg(0, 0x271, 8))),
    'LKAS_HEARTBIT': bool(fixture._tx(make_msg(0, 0x2d9, 5))),
  }
else:
  raise ValueError(case)
print(json.dumps(result, sort_keys=True))
