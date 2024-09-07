from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from searcherTool import tool_searcher
import pandas as pd
import re

import streamlit as st

st.set_page_config(page_title="Nurses demo", page_icon="👍")
st.title("Nurses demo")

import os 
import dotenv

dotenv.load_dotenv()
if os.getenv("OPENAI_API_KEY") is not None:
    openai_api_key = os.getenv("OPENAI_API_KEY")
else:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")


msgs = StreamlitChatMessageHistory()
memory = ConversationBufferMemory(
    chat_memory=msgs, return_messages=True, memory_key="chat_history", output_key="output"
)
if len(msgs.messages) == 0 or st.sidebar.button("Reset chat history"):
    msgs.clear()
    msgs.add_ai_message("How can I help you?")
    st.session_state.steps = {}

avatars = {"human": "user", "ai": "assistant"}
for idx, msg in enumerate(msgs.messages):
    with st.chat_message(avatars[msg.type]):
        # Render intermediate steps if any were saved
        for step in st.session_state.steps.get(str(idx), []):
            if step[0].tool == "_Exception":
                continue
            with st.status(f"**{step[0].tool}**: {step[0].tool_input}", state="complete"):
                st.write(step[0].log)
                st.write(step[1])
        st.write(msg.content)

if 'first' not in st.session_state:
    st.session_state.first = True

    App_names = ['APIFY', 'ASANA', 'ATTIO', 'BROWSERBASE_TOOL', 'BROWSER_TOOL', 'CLICKUP', 'CODEINTERPRETER', 'CODE_ANALYSIS_TOOL', 'CODE_FORMAT_TOOL', 'CODE_GREP_TOOL', 'CODE_INDEX_TOOL', 'CODE_MAP_TOOL', 'COMPOSIO', 'DISCORD', 'DISCORDBOT', 'DROPBOX', 'ELEVENLABS', 'EMBED_TOOL', 'EXA', 'FIGMA', 'FILETOOL', 'FIRECRAWL', 'GIT', 'GITHUB', 'GMAIL', 'GOOGLECALENDAR', 'GOOGLEDOCS', 'GOOGLEDRIVE', 'GOOGLEMEET', 'GOOGLESHEETS', 'GOOGLETASKS', 'GREPTILE', 'HACKERNEWS', 'HISTORY_FETCHER', 'HUBSPOT', 'IMAGE_ANALYSER', 'INDUCED_AI', 'JIRA', 'KLAVIYO', 'LINEAR', 'LISTENNOTES', 'MAILCHIMP', 'MATHEMATICAL', 'MULTIONAI', 'NASA', 'NOTION', 'PERPLEXITYAI', 'PIPEDRIVE', 'RAGTOOL', 'SCHEDULER', 'SERPAPI', 'SHELLTOOL', 'SLACK', 'SLACKBOT', 'SNOWFLAKE', 'SPIDERTOOL', 'SQLTOOL', 'TASKADE', 'TAVILY', 'TRELLO', 'TWITTER', 'TYPEFORM', 'WEATHERMAP', 'WEBTOOL', 'WORKSPACE_TOOL', 'YOUSEARCH', 'YOUTUBE', 'ZENDESK', 'ZEPTOOL']
    App_names = ', '.join(App_names)

    Tool_names = pd.read_csv('./tools/tools.csv')['tool'].to_numpy()
    Tool_names = ', '.join(Tool_names)

    prompt = """
    You are an AI model with access to a list of apps, each containing a variety of tools. Your role is to assist in breaking down commands and identifying the tools needed for execution. Your tasks are as follows:

    1. Rewrite the command into simpler, manageable steps suitable for a smaller model to handle.
    2. Identify the tools required by the smaller model, specifying which app each tool belongs to. You don't know the specific tools, so infer what might be necessary based on the apps available.
    
    Available Tools: {App_names}

    You understood? 
    """.format(App_names=App_names, Tool_names=Tool_names)

    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True)
    tools = []
    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
    executor = AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        response = executor.invoke(prompt, cfg)
        st.write(response["output"])
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]

if 'check' not in st.session_state:
    st.session_state.check = False

if prompt := st.chat_input(placeholder="Who won the Women's U.S. Open in 2018?"):
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()

    llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True, seed=42)
    tools = []
    chat_agent = ConversationalChatAgent.from_llm_and_tools(llm=llm, tools=tools)
    executor = AgentExecutor.from_agent_and_tools(
        agent=chat_agent,
        tools=tools,
        memory=memory,
        return_intermediate_steps=True,
        handle_parsing_errors=True,
    )
    with st.chat_message("assistant"):
        st_cb = StreamlitCallbackHandler(st.container(), expand_new_thoughts=False)
        cfg = RunnableConfig()
        cfg["callbacks"] = [st_cb]
        response = executor.invoke(prompt, cfg)
        st.write(response["output"])
        st.session_state.steps[str(len(msgs.messages) - 1)] = response["intermediate_steps"]

    if st.session_state.check == False:

        tools_needed = re.findall(r'\b[A-Z]+\b', response["output"])
        tools_needed = [tool_searcher(tool) for tool in tools_needed if len(tool) > 5]
        print(tools_needed)
        if len(tools_needed) > 0:
            st.session_state.check = True

        st.write("Are you good with these results?")
    
    else:

        if "yes" in prompt.lower():
            '''
            Make a neural network here
            '''
            print('LOL')    
        else:

            st.session_state.check = False
    