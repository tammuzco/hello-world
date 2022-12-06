# -*- coding: utf-8 -*-
# ------------------------------------------------------------------------------
#
#   Copyright 2021-2022 Valory AG
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
# ------------------------------------------------------------------------------
"""This module contains the round classes for register reset recovery."""

from enum import Enum
from typing import Dict, Optional, Tuple, Type, List

from packages.valory.skills.abstract_round_abci.base import (
    AbciApp,
    AbciAppTransitionFunction,
    AbstractRound,
    BaseSynchronizedData,
    CollectSameUntilThresholdRound,
)
from packages.valory.skills.register_reset_recovery_abci.payloads import RoundCountPayload


class Event(Enum):
    """Event enumeration for the Round Count round."""
    DONE = "done"
    ROUND_TIMEOUT = "round_timeout"

class RoundCountRound(CollectSameUntilThresholdRound):
    """A round in which the round count is stored as a list."""

    round_id = "round_count_round"
    allowed_tx_type = RoundCountPayload.transaction_type
    payload_attribute = "current_round_count"
    synchronized_data_class = BaseSynchronizedData

    def end_block(self) -> Optional[Tuple[BaseSynchronizedData, Event]]:
        """Process the end of the block."""
        if self.threshold_reached:
            # this simulates a state that is built across different round
            all_round_counts: List = self.synchronized_data.db.get("round_counts", [])
            all_round_counts.append(self.most_voted_payload)
            synchronized_data = self.synchronized_data.update(
                synchronized_data_class=self.synchronized_data_class,
                participants=self.collection,
                all_participants=self.collection,
                round_counts=all_round_counts,
            )
            return synchronized_data, Event.DONE
        return None


class RoundCountAbciApp(AbciApp[Event]):
    """RoundCountAbciApp that simply transitions to the same round infinitely."""

    initial_round_cls: Type[AbstractRound] = RoundCountRound
    transition_function: AbciAppTransitionFunction = {
        RoundCountRound: {
            Event.DONE: RoundCountRound,
        }
    }
    event_to_timeout: Dict[Event, float] = {
        Event.ROUND_TIMEOUT: 30.0,
    }
