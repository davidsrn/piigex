# log_scrubber.py: stream-process a log file, scrubbing PII line by line.
#
# Usage:
#   cat application.log | python examples/log_scrubber.py > scrubbed.log
#
# stable_tokens=True ensures the same PII value gets the same token within a run,
# which is useful for correlating log lines about the same entity.

import sys

from piigex import Scrubber
from piigex.tokens import TokenMap

_tm = TokenMap()
_scrubber = Scrubber(stable_tokens=True, token_map=_tm)

if __name__ == "__main__":
    for line in sys.stdin:
        sys.stdout.write(_scrubber.clean(line))
