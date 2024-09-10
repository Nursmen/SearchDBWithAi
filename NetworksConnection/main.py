
# Here we import all necessary stuff

from langchain.agents import ConversationalChatAgent, AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain_community.callbacks import StreamlitCallbackHandler
from langchain_community.chat_message_histories import StreamlitChatMessageHistory
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
from composio_crewai import App, ComposioToolSet, Action
from crewai import Agent, Task, Crew
from searcherTool import tool_searcher
from integrations import add_integration, check_integration
import pandas as pd
import re

import streamlit as st



# Here we prepare all necessary stuff

class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

st.set_page_config(page_title="Nurses demo", page_icon="👍")
st.title("Nurses demo")

import os 
import dotenv
from datetime import datetime

DATE = datetime.today().strftime("%Y-%m-%d")
TIMEZONE = datetime.now().astimezone().tzinfo

dotenv.load_dotenv()
if os.getenv("OPENAI_API_KEY") is not None:
    openai_api_key = os.getenv("OPENAI_API_KEY")
else:
    openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")







# In this part of the code we run crewai to actually run tools 

def run_crew(todo, tools, date, timezone):

    llm = ChatOpenAI(model="gpt-4o", openai_api_key=openai_api_key)

    general_agent = Agent(
        role="General Tool Agent",
        goal="""You take actions using APIs provided in the tool-set.""",
        backstory="""You are an AI agent responsible for taking actions using various tools provided to you. 
        You must utilize the correct APIs from the given tool-set based on the task at hand.""",
        verbose=True,
        tools=tools,  # List of tools (APIs) provided to the agent
        llm=llm,
        cache=False,
    )

    task = Task(
        description=f"Perform the following task: {todo}. Ensure you use the correct tool and schedule or manage the tasks appropriately. Today's date is {date} (in YYYY-MM-DD format) and the timezone is {timezone}.",
        agent=general_agent,
        expected_output="Successful completion of the task using the available tools.",
    )

    crew = Crew(agents=[general_agent], tasks=[task])
    result = crew.kickoff()
    print(result)

    return "Crew run initiated", 200





# Here we work with chat history

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





# Here is first run of the bot to give it some context

if 'first' not in st.session_state:
    st.session_state.first = True

    App_names = ['APIFY', 'ASANA', 'ATTIO', 'BROWSERBASE_TOOL', 'BROWSER_TOOL', 'CLICKUP', 'CODEINTERPRETER', 'CODE_ANALYSIS_TOOL', 'CODE_FORMAT_TOOL', 'CODE_GREP_TOOL', 'CODE_INDEX_TOOL', 'CODE_MAP_TOOL', 'COMPOSIO', 'DISCORD', 'DISCORDBOT', 'DROPBOX', 'ELEVENLABS', 'EMBED_TOOL', 'EXA', 'FIGMA', 'FILETOOL', 'FIRECRAWL', 'GIT', 'GITHUB', 'GMAIL', 'GOOGLECALENDAR', 'GOOGLEDOCS', 'GOOGLEDRIVE', 'GOOGLEMEET', 'GOOGLESHEETS', 'GOOGLETASKS', 'GREPTILE', 'HACKERNEWS', 'HISTORY_FETCHER', 'HUBSPOT', 'IMAGE_ANALYSER', 'INDUCED_AI', 'JIRA', 'KLAVIYO', 'LINEAR', 'LISTENNOTES', 'MAILCHIMP', 'MATHEMATICAL', 'MULTIONAI', 'NASA', 'NOTION', 'PERPLEXITYAI', 'PIPEDRIVE', 'RAGTOOL', 'SCHEDULER', 'SERPAPI', 'SHELLTOOL', 'SLACK', 'SLACKBOT', 'SNOWFLAKE', 'SPIDERTOOL', 'SQLTOOL', 'TASKADE', 'TAVILY', 'TRELLO', 'TWITTER', 'TYPEFORM', 'WEATHERMAP', 'WEBTOOL', 'WORKSPACE_TOOL', 'YOUSEARCH', 'YOUTUBE', 'ZENDESK', 'ZEPTOOL']
    App_names = ', '.join(App_names)

    Tool_names = pd.read_csv('./tools/tools.csv')['tool'].to_numpy()
    Tool_names = ', '.join(Tool_names)

    prompt = """
    You have 4 tools: GOOGLECALENDAR_CREATE_AN_EVENT, KLAVIYO_GET_COUPON, SLACK_LIST_APPROVED_APPS_FOR_ORG_OR_WORKSPACE, NOTION_CREATE_NOTION_PAGE.

    You should tell what tools another model should use to acomplish the task. When you return a tool name I will give that tool to another model. Just write what of 4 tools above fits the task best.
    Also rewrite humans command into your answer.

    When you get any input, just return one of 4 tools we gave you. Say yes if you understood?

    How it should work? 

    Input: List me all the repositories.
    \n Output: GITHUB_LIST_REPOSITORIES
    """

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





# Some initializations

if 'check' not in st.session_state:
    st.session_state.check = False

tools_needed = []



# Handle input

if prompt := st.chat_input(placeholder="Ask bot to do something..."):
    st.chat_message("user").write(prompt)

    if not openai_api_key:
        st.info("Please add your OpenAI API key to continue.")
        st.stop()


    # When we try to get right response

    if st.session_state.check == False:

        llm = ChatOpenAI(model_name="gpt-3.5-turbo", openai_api_key=openai_api_key, streaming=True, seed=42, temperature=0.5)
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

        st.session_state.response = response['output']

        tools_needed = re.findall(r'\b[A-Z_]+\b', response["output"])
        tools_needed = [tool_searcher.invoke(tool) for tool in tools_needed if len(tool) > 5]

        st.session_state.tools_needed = tools_needed
        st.session_state.prompt = prompt
    
        if len(tools_needed) > 0:
            st.session_state.check = True

            st.write("Are you good with these results?")
        else:
            st.write("Please provide more info")

    else:



    #   Ask user if he is good with the tools
    #   And if he is we run those tools

        if "yes" in prompt.lower() or 'ready' in prompt.lower():

            composio_toolset = ComposioToolSet()

 


            links = []
            apps = []
            for tool in st.session_state.tools_needed:

                app = tool.split('_')[0].lower()
                print(app)
                print(check_integration(app))

                if check_integration(app) == False: 

                    apps.append(app)
                    links.append(add_integration(app))

            if len(apps) == 0:
                tools = composio_toolset.get_tools(actions=[getattr(Action, tool) for tool in st.session_state.tools_needed])


                prompt = """
                You should use this tools:
                """ + st.session_state.response + " to " + st.session_state.prompt

                st.chat_message("user").write(prompt)



                with st.chat_message("assistant"):
                    stream_handler = StreamHandler(st.empty())
                    response, code = run_crew(todo=prompt, tools = tools, date=DATE, timezone=TIMEZONE)
                    
                    if code == 200:
                        st.write("Success! Now you can do something else!")

                    else:
                        st.write("Something went wrong. Please try again.")    

                st.session_state.check = False

            else:
                st.write("Please go to the following links:")
                for app, link in zip(apps, links):
                    st.markdown(f"[{app}]({link})")

                st.write("When you are ready, please type 'ready'")

        else:
            st.session_state.check = False