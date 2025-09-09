import streamlit as st
from openai import OpenAI
from streamlit.logger import get_logger
from utils import summary_generator
from utils.helper import check_availability
from utils.model_config import get_flattened_models, estimate_cost, get_model_recommendation, calculate_cost
import traceback
import requests
import json
import tempfile
from requests.auth import HTTPBasicAuth
import time
import os
import shutil

LOGGER = get_logger(__name__)

OPEN_AI_ORG_ID = st.secrets["OPENAI_ORG_ID"]
OPEN_AI_PROJECT_ID = st.secrets["OPENAI_API_PROJECT_ID"]
OPENAI_API_KEY = st.secrets["OPENAI_COMMISH_API_KEY"]

# Initialize client as None - will be created when needed
client = None

def get_openai_client():
    """Initialize OpenAI client when needed to avoid startup conflicts"""
    global client
    if client is None:
        try:
            # Import httpx to create a clean HTTP client
            import httpx
            http_client = httpx.Client(
                timeout=30.0,
                limits=httpx.Limits(max_keepalive_connections=1, max_connections=5)
            )
            client = OpenAI(
                organization=OPEN_AI_ORG_ID,
                project=OPEN_AI_PROJECT_ID,
                api_key=OPENAI_API_KEY,
                http_client=http_client
            )
        except Exception as e:
            # Fallback to basic client without HTTP client customization
            try:
                client = OpenAI(api_key=OPENAI_API_KEY)
            except Exception as e2:
                st.error(f"Failed to initialize OpenAI client: {e2}")
                return None
    return client

st.set_page_config(
    page_title="Commish.ai",
    page_icon="🏈",
    layout="centered",
    initial_sidebar_state="expanded"
)

def main():
    st.write("""
    ## Instructions:

    1. **Select your league type** from the sidebar.
    2. **Fill out the required fields** based on your league selection:
    - **ESPN**:
        - *League ID*: [Find it here](https://support.espn.com/hc/en-us/articles/360045432432-League-ID).
        - *SWID and ESPN_S2*: Use this [Chrome extension](https://chrome.google.com/webstore/detail/espn-private-league-key-a/bakealnpgdijapoiibbgdbogehhmaopn) or follow [manual steps](https://www.gamedaybot.com/help/espn_s2-and-swid/).
    - **Yahoo**:
        - *League ID*: Navigate to Yahoo Fantasy Sports → Click your league → Mouse over **League**, click **Settings**. The League ID number is listed first.
        - *Authenticate*: Follow the prompt to enter your authentication code. Then fill in the character description and trash talk levels as your normally would.
    - **Sleeper**:
        - *League ID*: [Find it here](https://support.sleeper.com/en/articles/4121798-how-do-i-find-my-league-id). 
    3. **Hit "🤖 Generate AI Summary"** to get your weekly summary.
    """)


    with st.sidebar:
        st.sidebar.image('./logo.png', use_container_width=True)
        is_available, today = check_availability()
        if is_available:
            st.success(f"Today is {today}. The most recent week is completed and a recap is available.")
        else:
            st.warning(
                "Recaps are best generated between Tuesday 4am EST and Thursday 7pm EST. "
                "Please come back during this time for the most accurate recap."
            )
        league_type = st.selectbox("Select League Type", ["Select", "ESPN", "Yahoo", "Sleeper"], key='league_type')

    if league_type != "Select":
        with st.sidebar.form(key='my_form'):
            if league_type == "ESPN":
                st.text_input("LeagueID", key='LeagueID')
                st.text_input("SWID", key='SWID', value='{D392D3A1-E320-49D8-A66E-6D0F3E81F42A}')
                st.text_input("ESPN_S2", key='ESPN2_Id', value='AEASaRdC%2BAe8Eop%2B2aNfcCeCZ%2FPFDhs2PXnoDtAIXENhz4zfIbfxnbqw5K%2Fqh0XJq1G9Rr2zHZDTD80z3bh38anzs8%2Brv82NZjSXVRQVsqVbt2hUHgHRN6QJ6ZC0I%2BPCoQ0ZMFZzFtahKMeWX2SYgRKXpWmg8eaVt0U5qYHen%2FLNmFeog0KhSzhcI8rZ2JlCT2Vm2WmOczjudQfMfbl%2B4i5%2FMQVV2CDZvjhIDbBrOQsAzI61dnknmSXZucBA7ZjaVxdparPU4BjNmwaV242dbzvT')
            elif league_type == "Yahoo":
                # Client_ID and Secret from https://developer.yahoo.com/apps/
                league_id = st.text_input("LeagueID", key='LeagueID')
                cid = st.secrets["YAHOO_CLIENT_ID"]
                cse = st.secrets["YAHOO_CLIENT_SECRET"]

                # Ensure that the Client ID and Secret are set
                if cid is None or cse is None:
                    st.error("Client ID or Client Secret is not set. Please set the YAHOO_CLIENT_ID and YAHOO_CLIENT_SECRET environment variables.")
                    st.stop()

                # URL for st button with Client ID in query string
                redirect_uri = "oob" #"oob"  # Out of band # "https://yahoo-ff-test.streamlit.app/" for dev version
                auth_page = f'https://api.login.yahoo.com/oauth2/request_auth?client_id={cid}&redirect_uri={redirect_uri}&response_type=code'

                # Show ST Button to open Yahoo OAuth2 Page
                if 'auth_code' not in st.session_state:
                    st.session_state['auth_code'] = ''

                if 'access_token' not in st.session_state:
                    st.session_state['access_token'] = ''

                if 'refresh_token' not in st.session_state:
                    st.session_state['refresh_token'] = ''
                
                temp_dir = None

                st.write("1. Click the link below to authenticate with Yahoo and get the authorization code.")
                st.write(f"[Authenticate with Yahoo]({auth_page})")

                # Get Auth Code pasted by user
                st.write("2. Paste the authorization code here:")
                auth_code = st.text_input("Authorization Code")

                if auth_code:
                    st.session_state['auth_code'] = auth_code
                    st.success('Authorization code received!')
                    #st.write(f'Your authorization code is: {auth_code}')

                # Get the token
                if st.session_state['auth_code'] and not st.session_state['access_token']:
                    basic = HTTPBasicAuth(cid, cse)
                    _data = {
                        'redirect_uri': redirect_uri,
                        'code': st.session_state['auth_code'],
                        'grant_type': 'authorization_code'
                    }

                    try:
                        r = requests.post('https://api.login.yahoo.com/oauth2/get_token', data=_data, auth=basic)
                        r.raise_for_status()  # Will raise an exception for HTTP errors
                        token_data = r.json()
                        st.session_state['access_token'] = token_data.get('access_token', '')
                        st.session_state['refresh_token'] = token_data.get('refresh_token', '')
                        st.session_state['token_time'] = time.time()
                        st.success('Access token received!')
                    except requests.exceptions.HTTPError as err:
                        st.error(f"HTTP error occurred: {err}")
                    except Exception as err:
                        st.error(f"An error occurred: {err}")

                # Use the access token
                if st.session_state['access_token']:
                    #st.write("Now you can use the access token to interact with Yahoo's API.")

                    # Allow user to input league ID
                    # league_id = st.text_input("Enter your Yahoo Fantasy Sports league ID:")
                    temp_dir = tempfile.mkdtemp()
                    if league_id:
                        # Define the paths to the token and private files
                        token_file_path = os.path.join(temp_dir, "token.json")
                        private_file_path = os.path.join(temp_dir, "private.json")

                        # Create the token file with all necessary details
                        token_data = {
                            "access_token": st.session_state['access_token'],
                            "consumer_key": cid,
                            "consumer_secret": cse,
                            "guid": None,
                            "refresh_token": st.session_state['refresh_token'],
                            "expires_in": 3600, 
                            "token_time": st.session_state['token_time'],
                            "token_type": "bearer"
                            }
                        with open(token_file_path, 'w') as f:
                            json.dump(token_data, f)

                        # Create the private file with consumer key and secret
                        private_data = {
                            "consumer_key": cid,
                            "consumer_secret": cse,
                        }
                        with open(private_file_path, 'w') as f:
                            json.dump(private_data, f)
            elif league_type == "Sleeper":
                st.text_input("LeagueID", key='LeagueID', value='1257120279386148864')
            
            st.text_input("Character Description", key='Character Description', placeholder="Dwight Schrute", help= "Describe a persona for the AI to adopt. E.g. 'Dwight Schrute' or 'A very drunk Captain Jack Sparrow'")
            st.slider("Trash Talk Level", 1, 10, key='Trash Talk Level', value=5, help="Scale of 1 to 10, where 1 is friendly banter and 10 is more extreme trash talk")
            
            # Model selection dropdown with pricing information
            model_options = get_flattened_models()
            selected_model_display = st.selectbox(
                "AI Model", 
                options=[option[0] for option in model_options],
                index=1,  # Default to gpt-4o-mini (index 1)
                key='selected_model_display',
                help="Choose the AI model for generating your summary. GPT-4o Mini offers the best balance of creativity and cost for fantasy football summaries."
            )
            
            # Extract the actual model ID from the selected display option
            selected_model_id = next(option[1] for option in model_options if option[0] == selected_model_display)
            
            # Show model recommendation badge
            recommendation = get_model_recommendation(selected_model_id)
            if recommendation["badge"]:
                st.caption(f"{recommendation['badge']} - {recommendation['reason']}")
            
            # Show estimated cost for typical summary
            estimated_cost_info = estimate_cost("Sample fantasy football league summary with stats and team information", 800, selected_model_id)
            if "estimated_total_cost" in estimated_cost_info:
                st.caption(f"💰 Estimated cost: ~${estimated_cost_info['estimated_total_cost']:.4f} for typical summary")
            
            submit_button = st.form_submit_button(label='🤖 Generate AI Summary')

    
        # Handling form 
        if submit_button:
            try:
                progress = st.progress(0)
                progress.text('Starting...')
                
                required_fields = ['LeagueID', 'Character Description', 'Trash Talk Level']
                if league_type == "ESPN":
                    required_fields.extend(['SWID', 'ESPN2_Id'])
                
                # Input validation
                progress.text('Validating credentials...')
                progress.progress(5)
                for field in required_fields:
                    value = st.session_state.get(field, None)
                    if not value:
                        st.error(f"{field} is required.")
                        return  # Stop execution if any required field is empty
                
                league_id = st.session_state.get('LeagueID', 'Not provided')
                character_description = st.session_state.get('Character Description', 'Not provided')
                trash_talk_level = st.session_state.get('Trash Talk Level', 'Not provided')
                swid = st.session_state.get('SWID', 'Not provided')
                espn2 = st.session_state.get('ESPN2_Id', 'Not provided')

                # Moderate the character description
                progress.text('Validating character...')
                progress.progress(15)
                # if not summary_generator.moderate_text(client, character_description):
                #     st.error("The character description contains inappropriate content. Please try again.")
                #     return  # Stop execution if moderation fails
                
                # Fetching league summary
                progress.text('Fetching league summary...')
                progress.progress(30)
                if league_type == "ESPN":
                    LOGGER.debug("Attempting ESPN summary generator...")
                    summary, debug_info = summary_generator.get_espn_league_summary(
                        league_id, espn2, swid 
                    )
                    LOGGER.debug("~~ESPN DEBUG BELOW~~")
                    LOGGER.debug(debug_info)
                    LOGGER.debug("~~ESPN SUMMARY BELOW~~")
                    LOGGER.debug(summary)
                elif league_type == "Yahoo":
                    summary = summary_generator.get_yahoo_league_summary(league_id, temp_dir)
                    LOGGER.debug(summary)
                    st.write("Completed summary query, cleaning up...")
                    shutil.rmtree(temp_dir)
                    st.write("Done with cleanup! Creating AI summary now...")
                elif league_type == "Sleeper":
                    auth_directory = "auth"
                    summary = summary_generator.generate_sleeper_summary(
                        league_id  
                    )
                    LOGGER.debug(summary)
                    LOGGER.info(f"Generated Sleeper Summary: \n{summary}")
                    st.write(summary) #to delete
                
                progress.text('Generating AI summary...')
                progress.progress(50)

                LOGGER.debug("Initializing GPT Summary Stream...")
                try:
                    openai_client = get_openai_client()
                    if openai_client is None:
                        st.error("Failed to initialize OpenAI client")
                        return
                    
                    gpt4_summary_stream = summary_generator.generate_gpt4_summary_streaming(
                        openai_client, summary, character_description, trash_talk_level, selected_model_id
                    )
                    LOGGER.debug(f"Generator object initialized: {gpt4_summary_stream}")
                    
                    with st.chat_message("Commish", avatar="🤖"):
                        message_placeholder = st.empty()  # Placeholder for streamed message
                        full_response = ""  # Variable to store the full response as it streams
                        usage_info = None  # Store usage data for cost calculation
                
                        # Iterate over the generator streaming responses
                        for chunk in gpt4_summary_stream:
                            # Ensure that 'chunk' is not None before processing
                            if chunk is not None:
                                # Check if this chunk contains usage data
                                if chunk.startswith("__USAGE_DATA__") and chunk.endswith("__"):
                                    LOGGER.debug(f"Found usage data chunk: {chunk}")
                                    # Parse usage data: __USAGE_DATA__prompt,completion,total__model__
                                    parts = chunk.replace("__USAGE_DATA__", "").replace("__", "").split("__")
                                    if len(parts) >= 2:
                                        tokens = parts[0].split(",")
                                        model_used = parts[1]
                                        if len(tokens) == 3:
                                            # Create usage object-like structure
                                            class UsageData:
                                                def __init__(self, prompt, completion, total):
                                                    self.prompt_tokens = int(prompt)
                                                    self.completion_tokens = int(completion)
                                                    self.total_tokens = int(total)
                                            
                                            usage_info = {
                                                "usage": UsageData(tokens[0], tokens[1], tokens[2]),
                                                "model": model_used
                                            }
                                            LOGGER.debug(f"Parsed usage info: {usage_info}")
                                elif chunk.startswith("__USAGE_DATA_FALLBACK__") and chunk.endswith("__"):
                                    # Handle fallback case with estimated tokens
                                    LOGGER.debug(f"Found fallback usage data: {chunk}")
                                    parts = chunk.replace("__USAGE_DATA_FALLBACK__", "").replace("__", "").split("__")
                                    if len(parts) >= 2:
                                        estimated_output = int(parts[0])
                                        model_used = parts[1]
                                        # Estimate input tokens from the instruction length
                                        estimated_input = len(str(character_description) + str(trash_talk_level) + str(summary)) // 4
                                        
                                        class UsageData:
                                            def __init__(self, prompt, completion, total):
                                                self.prompt_tokens = int(prompt)
                                                self.completion_tokens = int(completion)
                                                self.total_tokens = int(total)
                                        
                                        usage_info = {
                                            "usage": UsageData(estimated_input, estimated_output, estimated_input + estimated_output),
                                            "model": model_used,
                                            "estimated": True
                                        }
                                        LOGGER.debug(f"Created fallback usage info: {usage_info}")
                                else:
                                    # Regular content chunk
                                    full_response += chunk  # Append each streamed chunk to the full response
                                    message_placeholder.markdown(full_response + "▌")  # Display partial message with a cursor-like symbol
                                    LOGGER.debug(f"Received chunk: {chunk}")  # Log each chunk for debugging
                            
                        # Once streaming is done, update the message with the complete response
                        message_placeholder.markdown(full_response)
                
                    LOGGER.debug("GPT Stream completed!")
                    
                    # Display cost information if usage data is available
                    if usage_info and "usage" in usage_info:
                        cost_info = calculate_cost(usage_info["usage"], usage_info["model"])
                        if "total_cost" in cost_info:
                            # Check if this is estimated data
                            is_estimated = usage_info.get("estimated", False)
                            st.success("✅ **Summary Generated Successfully!**")
                            
                            # Create cost breakdown display
                            col1, col2 = st.columns(2)
                            with col1:
                                st.metric("📊 Total Tokens", f"{cost_info['total_tokens']:,}")
                                st.metric("💰 Total Cost", f"${cost_info['total_cost']:.6f}")
                            
                            with col2:
                                st.metric("📝 Input Tokens", f"{cost_info['prompt_tokens']:,}")
                                st.metric("🎯 Output Tokens", f"{cost_info['completion_tokens']:,}")
                            
                            # Show detailed breakdown
                            with st.expander("💳 **Cost Breakdown**"):
                                st.write(f"**Model Used:** {usage_info['model']}")
                                if is_estimated:
                                    st.warning("⚠️ **Note:** Token counts are estimated (actual usage tracking unavailable)")
                                st.write(f"**Input Cost:** ${cost_info['prompt_cost']:.6f} ({cost_info['prompt_tokens']:,} tokens)")
                                st.write(f"**Output Cost:** ${cost_info['completion_cost']:.6f} ({cost_info['completion_tokens']:,} tokens)")
                                
                                # Show cost comparison with other models
                                if usage_info['model'] == 'gpt-4o-mini':
                                    st.info("💡 **Great choice!** GPT-4o Mini offers excellent creativity at a budget-friendly price.")
                                elif usage_info['model'] in ['gpt-5', 'gpt-4o']:
                                    savings_vs_gpt5 = (0.012 - cost_info['total_cost']) if cost_info['total_cost'] < 0.012 else 0
                                    if savings_vs_gpt5 > 0:
                                        st.info(f"💰 **You saved ~${savings_vs_gpt5:.4f}** compared to premium models!")
                    else:
                        # Fallback: Show a simple message if no usage data was captured
                        LOGGER.warning("No usage info available for cost display")
                        st.info("💡 **Summary generated successfully!** Cost tracking temporarily unavailable - trying to capture usage data in future versions.")
                    
                    # Optionally, provide the full response in a code block with a copy button
                    st.markdown("**Click the copy icon** 📋 below in top right corner to copy your summary and paste it wherever you see fit!")
                    st.code(full_response, language="")
                
                except Exception as e:
                    LOGGER.error(f"An error occurred while streaming GPT response: {str(e)}")
                    error_str = str(e)
                    
                    # Display user-friendly error messages for OpenAI API issues
                    if "insufficient_quota" in error_str or "429" in error_str:
                        st.error("⚠️ **OpenAI API Quota Exceeded**\n\nYour OpenAI API credits have been exhausted. Please check your billing plan at [OpenAI Platform](https://platform.openai.com/billing) or try again later.")
                    elif "401" in error_str or "unauthorized" in error_str.lower():
                        st.error("🔐 **OpenAI API Authentication Failed**\n\nThe API key appears to be invalid or expired. Please contact support to resolve this issue.")
                    elif "503" in error_str or "service_unavailable" in error_str:
                        st.error("🔧 **OpenAI Service Unavailable**\n\nOpenAI's service is temporarily unavailable. Please try again in a few minutes.")
                    elif "rate_limit" in error_str.lower() or "too_many_requests" in error_str.lower():
                        st.error("⏱️ **Rate Limit Exceeded**\n\nToo many requests have been made recently. Please wait a moment and try again.")
                    else:
                        st.error(f"❌ **Unexpected Error**\n\nSomething went wrong while generating your summary. Please try again later.")
                    
                    # Only show detailed error in debug mode
                    if st.session_state.get('debug_mode', False):
                        with st.expander("Debug Information"):
                            st.text(traceback.format_exc())
                    
                    LOGGER.exception(e)
                    
                LOGGER.debug("GPT Stream done!")
                progress.text('Done!')
                progress.progress(100)
                
            except Exception as e:
                LOGGER.error(f"An error occurred in main form processing: {str(e)}")
                error_str = str(e)
                
                # Handle common errors gracefully
                if "league not found" in error_str.lower() or "invalid league" in error_str.lower():
                    st.error("🏈 **League Not Found**\n\nThe league ID you provided could not be found. Please double-check your league ID and try again.")
                elif "authentication" in error_str.lower() or "invalid credentials" in error_str.lower():
                    st.error("🔐 **Authentication Failed**\n\nThere was an issue with your login credentials. Please verify your information and try again.")
                elif "network" in error_str.lower() or "connection" in error_str.lower():
                    st.error("🌐 **Network Error**\n\nUnable to connect to the fantasy sports service. Please check your internet connection and try again.")
                else:
                    st.error("❌ **Something Went Wrong**\n\nAn unexpected error occurred while processing your request. Please try again.")
                
                # Only show detailed error in debug mode
                if st.session_state.get('debug_mode', False):
                    with st.expander("Debug Information"):
                        st.text(traceback.format_exc())
                
                LOGGER.exception(e)

if __name__ == "__main__":
    main()


