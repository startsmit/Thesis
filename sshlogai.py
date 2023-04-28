import openai

# Set up the OpenAI API credentials
openai.api_key = ""

# Define the path to the log file
log_file_path = r"S:\Thesis\OpenSSH_2k.log"

# Define the GPT-Neo API parameters
engine = "text-davinci-003"
model = "text-davinci-003"
input_prefix = "Parse the following Parse the following Openssh log entry and extract any relevant fields:- Date- Day -Time - Component - Pid - Content. For example this OpenSSH log - \"Dec 10 06:55:46 LabSZ sshd[24200]: reverse mapping checking getaddrinfo for ns.marryaldkfaczcz.com [173.234.31.186] failed - POSSIBLE BREAK-IN ATTEMPT! \" can be parsed as { \"Date\":Dec,\"Day\":10,\"Time\": 06:55:46,\"Component\": LabSZ,\"Pid\": 24200,\"Content\": reverse mapping checking getaddrinfo for ns.marryaldkfaczcz.com [173.234.31.186] failed - POSSIBLE BREAK-IN ATTEMPT!}"
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

        # Check if parsed log matches expected format
        if '\"Date\":' in parsed_log and '\"Day\":' in parsed_log and '\"Time\":' in parsed_log and '\"Component\":' in parsed_log and '\"Pid\":' in parsed_log and '\"Content\":' in parsed_log:
            # Extract Date, Day, Time, Component, Pid and Content from parsed log
            date_str = str(parsed_log.split('\"Date\":')[1].split(',')[0]).strip('"')
            day_str = str(parsed_log.split('\"Day\":')[1].split(',')[0])
            time_str = str(parsed_log.split('\"Time\":')[1].split(',')[0]).strip('"')
            component_str = str(parsed_log.split('\"Component\":')[1].split(',')[0]).strip('"')
            pid_str = str(parsed_log.split('\"Pid\":')[1].split(',')[0])
            content_start_index = parsed_log.find('"Content":') + len('"Content":')
            content_end_index = parsed_log.find('}', content_start_index)
            content_str = str(parsed_log.split('\"Content\":')[1].strip().rstrip('}')).strip('"')

            formatted_log = f"{date_str} {day_str} {time_str} {component_str} sshd[{pid_str}]: {content_str}"
        else:
            # Return original log message without formatting
            formatted_log = log_message
        # Write the parsed log to the parsed_logs_file
        with open('ssh_parsed_logs.log', "a") as parsed_logs_file:
            parsed_logs_file.write(parsed_log + "\n")

        return formatted_log
    except Exception as e:
        # Log any errors that occur
        print(str(e))
        return "[null] [null] no content"

# Open the log file and iterate over its lines
with open(log_file_path,'r',encoding="utf-8") as log_file:
    # Open the output file for writing
    with open('ssh_formatted_logs.log', 'w') as output_file:
        for line in log_file:
            # Strip any leading/trailing white space from the log message
            log_message = line.strip()
            print(log_message + "\n")
            # Extract logs in desired format
            formatted_log = extract_logs(log_message)
            if formatted_log:
                # Write the formatted log to the output file
                output_file.write(formatted_log + '\n')
