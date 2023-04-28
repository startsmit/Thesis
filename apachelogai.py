import openai

# Set up the OpenAI API credentials
openai.api_key = ""

# Define the path to the log file
log_file_path = r"S:\Thesis\Apache_2k.log"

# Define the GPT-Neo API parameters
engine = "text-davinci-003"
model = "text-davinci-003"
input_prefix = "Parse the following Parse the following Apache log entry and extract any relevant fields:- time - level - content. For example this apache log -\"[Thu Jun 09 06:07:04 2005] [notice] LDAP: Built with OpenLDAP LDAP SDK\" can be parsed as { \"Time\":[Thu Jun 09 06:07:04 2005], \"Level\":[notice], \"Content\": LDAP: Built with OpenLDAP LDAP SDK }"
max_tokens = 300
n = 1
stop = None
temperature = 0

# Function to extract logs in desired format
def extract_logs(log_message):
    try:
        # Extract features from the log message using GPT-3
        response = openai.Completion.create(
            engine=engine,
            prompt=input_prefix + "\n" + log_message,
            max_tokens=max_tokens,
            n=n,
            stop=stop,
            temperature=temperature,
        )

        # Extract the relevant fields from the response
        parsed_log = response.choices[0].text.strip()
      
    #
        # Check if parsed log matches expected format
        if '\"Time\":[' in parsed_log and '\"Level\":[' in parsed_log and '\"Content\": ' in parsed_log:
            # Extract time, level and content from parsed log
            time_str = str(parsed_log.split('\"Time\":[')[1].split('], ')[0])
            level_str = str(parsed_log.split('\"Level\":[')[1].split('], ')[0])
            content_str = str(parsed_log.split('\"Content\": ')[1].strip().rstrip('}'))

            # Format log in desired format
            formatted_log = f"[{time_str}] [{level_str}] {content_str}"
        else:
            # Return original log message without formatting
            formatted_log = "[null] [null] no content"
        
        with open('apache_parsed_logs.log', "a") as parsed_logs_file:
            parsed_logs_file.write(parsed_log + "\n")

        return formatted_log
    except Exception as e:
        # Log any errors that occur
        print(str(e))
        return "[null] [null] no content"

# Open the log file and iterate over its lines
with open(log_file_path,'r',encoding="utf-8") as log_file:
    # Open the output file for writing
    with open('apache_formatted_logs.log', 'w') as output_file:
        for line in log_file:
            # Strip any leading/trailing white space from the log message
            log_message = line.strip()
            print(log_message + "\n\n")
            # Extract logs in desired format
            formatted_log = extract_logs(log_message)
            if formatted_log:
                # Write the formatted log to the output file
                output_file.write(formatted_log + '\n')
