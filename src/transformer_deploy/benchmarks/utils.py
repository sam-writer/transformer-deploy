#  Copyright 2021, Lefebvre Sarrut Services
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

import logging
import time
from collections import OrderedDict
from contextlib import contextmanager
from typing import Dict, List, Tuple

import numpy as np
import torch


def print_timings(name: str, timings: List[float]):
    mean_time = 1e3 * np.mean(timings)
    std_time = 1e3 * np.std(timings)
    min_time = 1e3 * np.min(timings)
    max_time = 1e3 * np.max(timings)
    median, percent_95_time, percent_99_time = 1e3 * np.percentile(timings, [50, 95, 99])
    print(
        f"[{name}] "
        f"mean={mean_time:.2f}ms, "
        f"sd={std_time:.2f}ms, "
        f"min={min_time:.2f}ms, "
        f"max={max_time:.2f}ms, "
        f"median={median:.2f}ms, "
        f"95p={percent_95_time:.2f}ms, "
        f"99p={percent_99_time:.2f}ms"
    )


def setup_logging(level: int = logging.INFO):
    logging.basicConfig(format="%(asctime)s %(levelname)-8s %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=level)


@contextmanager
def track_infer_time(buffer: [int]):
    start = time.perf_counter()
    yield
    end = time.perf_counter()
    buffer.append(end - start)


def prepare_input(
    seq_len: int, batch_size: int, include_token_ids: bool
) -> Tuple[Dict[str, torch.Tensor], Dict[str, np.ndarray]]:
    shape = (batch_size, seq_len)
    inputs_pytorch: OrderedDict[str, torch.Tensor] = OrderedDict()
    inputs_pytorch["input_ids"] = torch.randint(high=100, size=shape, dtype=torch.long, device="cuda")
    if include_token_ids:
        inputs_pytorch["token_type_ids"] = torch.ones(size=shape, dtype=torch.long, device="cuda")
    inputs_pytorch["attention_mask"] = torch.ones(size=shape, dtype=torch.long, device="cuda")
    inputs_onnx: Dict[str, np.ndarray] = {
        k: np.ascontiguousarray(v.detach().cpu().numpy()) for k, v in inputs_pytorch.items()
    }
    return inputs_pytorch, inputs_onnx
