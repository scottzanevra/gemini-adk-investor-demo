# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Data Science Agent V2: generate nl2py and use code interpreter to run the code."""
import os
from google.adk.code_executors import VertexAiCodeExecutor
from google.adk.agents import Agent

from stock_agent.sub_agents.analytics_agent.prompts import return_instructions_analytics
from stock_agent.sub_agents.analytics_agent.tools import get_historical_yahoo_finance

root_agent = Agent(
    model="gemini-2.0-flash",
    name="analytics_agent",
    instruction=return_instructions_analytics(),
    description=(
        """
        Your go-to expert for doing analytics and charting activities on a users behalf.  
        Use the get historical data tool to retrive the historical data for a given stock. 
        this will be sue for th analytics
        """
    ),
    code_executor=VertexAiCodeExecutor(
        optimize_data_file=True,
        stateful=True,
    ),
    tools=[get_historical_yahoo_finance]
)
