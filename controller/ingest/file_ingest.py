#  Copyright 2024 IBM, Inc.
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

import json
import logging
import re
from string import Template

from common.signal import Signal, Signals
from common.configuration_api import IngestSubType


logger = logging.getLogger(__name__)


def enrich_metric_signature_info(json_signal):
    signature_info = {}
    signature_info["first_time"] = json_signal["values"][0][0]
    signature_info["last_time"] = json_signal["values"][-1][0]
    signature_info["num_of_items"] = len(json_signal["values"])
    signature_info["__name__"] = json_signal["metric"]["__name__"]
    json_signal["metric"]["signature_info"] = signature_info


def ingest(ingest_config):
    signals = Signals()
    ingest_file = ingest_config.file_name
    ingest_name_template = ingest_config.ingest_name_template
    ingest_filter_metadata = ingest_config.filter_metadata

    signals.metadata["ingest_type"] = IngestSubType.PIPELINE_INGEST_FILE.value
    signals.metadata["ingest_source"] = ingest_file
    metrics_metadata = []

    logger.info(f"Reading signals from {ingest_file}")
    try:
        with open(ingest_file, 'r') as file:
            data = json.load(file)
    except Exception as e:
        err = f"The file {ingest_file} does not exist {e}"
        raise RuntimeError(err) from e
    json_signals = data["data"]["result"]
    for signal_count, json_signal in enumerate(json_signals):
        if 'metric' in json_signal.keys():
            signal_type = "metric"
            enrich_metric_signature_info(json_signal)
            if ingest_name_template != "":
                # adding `count` to allow usage by template
                json_signal["metric"]["count"] = signal_count
                # save original signal name into `original_name` if needed
                if "__name__" in json_signal["metric"]:
                    json_signal["metric"]["original_name"] = json_signal["metric"]["__name__"]
                # build new name based on template
                json_signal["metric"]["__name__"] = Template(
                    ingest_name_template).safe_substitute(json_signal["metric"])
            signal_metadata = json_signal["metric"]
            signal_time_series = json_signal["values"]
            metrics_metadata.append(signal_metadata)

        else:
            raise Exception("Ingest: signal type - Not implemented")

        # filter signals based on ingest_filter_metadata (if exists)
        if ingest_filter_metadata:
            match = re.search(ingest_filter_metadata, str(signal_metadata))
            if match is None:
                continue

        signals.append(Signal(type=signal_type,
                              metadata=signal_metadata,
                              time_series=signal_time_series))
    signals.metadata["metrics_metadata"] = metrics_metadata
    return signals
