from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, ChatMessage

# from langchain.tools import format_tool_to_openai_function, StructuredTool
from langchain.agents import tool
from langchain.tools.render import format_tool_to_openai_function

from langchain.embeddings import OpenAIEmbeddings
from constants import COLORS

from langchain.vectorstores import Chroma
# vectordb = Chroma(embedding_function=OpenAIEmbeddings())
import json

from dotenv import load_dotenv

load_dotenv()


def system_message():
    message = """
    You are in charge of making decisions for an NPC in a simulation. 
    You will be given context about the NPC and the game world and you will have access to a list 
    actions you can queue. You have a list of available functions you can call with arguments. 
    Calling a function adds that particular action to the NPCs current queue. Only respond by making function
    calls. With each response, give your reasoning for why you chose that action and make a function call.
    If an action fails or something goes wrong try to figure out why it went wrong and then try to make decisions to fix it.
    """
    return message

def get_context(npc, game_map, all_npcs, last_actions):
    # get NPC location, available locations, statuses
    current_location_name = game_map.get_current_location(npc.x, npc.y)
    available_locations = game_map.get_available_locations(npc.x, npc.y)
    available_npcs = available_npcs = [n.name for n in all_npcs if n != npc]
    available_locations = [l.full_name() for l in available_locations]
    actions = [a for a in npc.action_queue]
    action_string = ""
    for a in actions:
        action_string += f"type: {a.type}"
        if a.target:
            action_string += f", target: {a.target.name}"
        if a.message:
            action_string += f", message: {a.message}"
        action_string += "\n"
    if not action_string: action_string = "None"
    paused_action = "None"
    if npc.paused_action:
        paused_action = f"type: {npc.paused_action.type}"
        if npc.paused_action.target:
            paused_action += f", target: {npc.paused_action.target.name}"
        if npc.paused_action.message:
            paused_action += f", message: {npc.paused_action.message}"
    last_actions_str = ""
    for a in last_actions:
        last_actions_str += str(a) +"\n"
    if not last_actions_str: last_actions_str = "None"

    logs = npc.logs[-3:]
    game_logs_str = ""
    for log in logs:
        game_logs_str+=log
        game_logs_str+="\n"
    

    # Last 3 performed actions:
    # {last_actions_str}
    context = f"""
    NPC name: {npc.name}
    Current Location: {current_location_name}
    Available Locations to pathfind to: {available_locations}
    Available NPCs to pathfind/converse to: {available_npcs}

    Current Statuses
    Hunger: {npc.hunger} (higher value means more satiated, lower value means more hungry)
    Food: {npc.food} (needed to fill hunger)
    Currency: {npc.currency} (needed to buy food)
    Social: {npc.social} (decreases the longer NPCs go without conversing)

    Actions currently in queue (in order): 
    {action_string}

    Paused action if any:
    {paused_action}

    Most recent game logs:
    {game_logs_str}
    """
    return context

# TODO: build parser for function call to action queue

@tool
def buy_food():
    """
    buy food
    """
    pass

@tool
def converse(target, message):
    """
    target: MUST BE THE NAME OF AN NPC
    message: what to say 
    """
    pass

@tool
def pathfind(target):
    """
    Use this function to move to different places in the game,
    get closer to other NPCs etc.
    target: this can be the name of a location that you can pathfind to, or the name of another NPC
    """
    pass

@tool
def do_job():
    """
    do your job
    """
    pass

@tool
def eat():
    """
    eat food
    """
    pass

@tool
def activity(message):
    """
    Perform an activity that is not listed.
    message: a string saying what the npc does (e.g. "reads a book")
    """

@tool
def queue_multiple_actions(actions:list[dict]):
    """
    Use this function to queue multiple actions.
    actions should be a list of function calls. 
    each function call should have the name of the function
    and the arguments to pass to that function 
    """
    pass

def get_logs():
    # get NPC logs since last call
    pass
import openai

def prompt(npc, game_map, all_npcs, last_actions):
    # used by decide action and converse
    # converse_tool = StructuredTool.from_function(converse)
    # pathfind_tool = StructuredTool.from_function(pathfind)
    # food_tool = StructuredTool.from_function(buy_food)
    # eat_tool = StructuredTool.from_function(eat)
    # job_tool = StructuredTool.from_function(do_job)


    tools = [converse, pathfind, buy_food, eat, do_job, activity]
    # tools = [converse_tool, pathfind_tool, food_tool, eat_tool, job_tool]
    functions = [format_tool_to_openai_function(t) for t in tools]
    tools=[{"type":"function", "function":f} for f in functions]
    # chat = ChatOpenAI(model="gpt-3.5-turbo-1106")
    chat = ChatOpenAI(model="gpt-3.5-turbo")
    if not npc.reasoning_history:
        messages = [SystemMessage(content=system_message()), SystemMessage(content=get_context(npc, game_map, all_npcs, last_actions))]
    else:
        sys = npc.reasoning_history.pop(0)
        npc.reasoning_history = [sys] + npc.reasoning_history[-6:]
        messages = npc.reasoning_history
        logs = npc.logs
        game_logs_str = "GAME LOGS:\n"
        for log in logs:
            game_logs_str+=log
            game_logs_str+="\n"
        messages.append(SystemMessage(content=game_logs_str))
        messages.append(SystemMessage(content=get_context(npc, game_map, all_npcs, last_actions)))
        npc.clear_logs()
    action, args = None, None
    while check_valid_args(action, args, all_npcs, game_map):
        AI_message = chat.predict_messages(messages, functions=functions)
        messages.append(AI_message)
        action = AI_message.additional_kwargs.get('function_call')
        if action is None: 
            messages.append(SystemMessage(content = "No action has been selected"))
            continue
        args = json.loads(action.get('arguments'))
        
        if check_valid_args(action, args, all_npcs, game_map):
            messages.append(ChatMessage(
                role='function',
                additional_kwargs = {'name': action},
                content = "The chosen arguments are not valid"
            ))
        min()
        pass
    
    npc.reasoning_history = messages
    return {'type': action['name'], **args}

def check_valid_args(action, args, all_npcs, game_map):
    if action is None: return True
    
    target_npc = None
    target = args.get('target')
    if target is None: return False
    for npc in all_npcs:
        if npc.name == target:
            target_npc = npc
            break
    loc = target.split(':')[-1]
    target_location = game_map._find_location_by_name(loc)

    if action == "converse" and target_npc is None:
        return True

    if action == "pathfind" and target_npc is None and target_location is None:
        return True 
    return False

def converse_message(npc, game_map, all_npcs, last_actions):
    # used by decide action and converse
    # converse_tool = StructuredTool.from_function(converse)
    # pathfind_tool = StructuredTool.from_function(pathfind)
    # food_tool = StructuredTool.from_function(buy_food)
    # eat_tool = StructuredTool.from_function(eat)
    # job_tool = StructuredTool.from_function(do_job)

    system_prompt = """
    Right now you are in a conversation with another NPC. Based on what they say, talk back to them. 
    If you want to end the conversation, respond with a <eos> token at the end of your response (This is optional).
    """
    
    # chat = ChatOpenAI(model="gpt-3.5-turbo-1106")
    chat = ChatOpenAI(model="gpt-3.5-turbo")
    messages = [SystemMessage(content=system_message()+"\n"+get_context(npc, game_map, all_npcs, last_actions)), SystemMessage(content=system_prompt)]
    for message in npc.current_conversation:
        content = ":".join(message.split(":")[1:]).strip()
        if npc.name == message.split(":")[0]:
            messages.append(AI_message(content=content))
        else:
            messages.append(HumanMessage(content=content))
    
    AI_message = chat.predict_messages(messages)
    end = False
    content = AI_message.content
    if "<eos>" in content:
        content = content.replace("<eos>","")
        end = True

    return content, end
    