import csv
import openai

# Set up the OpenAI API credentials
openai.api_key = ""

# Define the path to the log file and output file
log_file_path = r"C:\Users\91910\Downloads\logai-20230310T063957Z-001\logai\Apache.log"
output_file_path = r"C:\Users\91910\Downloads\logai-20230310T063957Z-001\logai\parsed_logs.csv"

# Define the GPT-Neo API parameters
engine = "text-davinci-003"
model = "text-davinci-003"
input_prefix = "Parse the following Parse the following Apache log entry and extract any relevant fields:- - Date - Time - Log Level - Module - Client IP Address (if present) - HTTP Request Method (if present)- HTTP Request Path (if present)- Message"
max_tokens = 300
n = 1
stop = None
temperature = 0.5

# Open the log file and CSV output file
with open(log_file_path,'r',encoding="utf-8") as log_file, open(output_file_path, 'w', newline='') as output_file:
    # Create a CSV writer object
    writer = csv.writer(output_file)
    
    # Write the header row to the CSV file
    writer.writerow(['Date', 'Time', 'Log Level', 'Module', 'Client IP Address', 'HTTP Request Method', 'HTTP Request Path', 'Message'])
    
    # Iterate over the lines in the log file
    for line in log_file:
        # Strip any leading/trailing white space from the log message
        log_message = line.strip()
        print(log_message + "\n\n")   
        
        # Extract features from the log message using GPT-Neo
        response = openai.Completion.create(
            engine=engine,
            prompt=input_prefix + "\n" + log_message,
            max_tokens=max_tokens,
            n=n,
            stop=stop,
            temperature=temperature,
        )
        
        # Parse the extracted features
        parsed_log = response.choices[0].text.strip().split('\n')
        parsed_log = [field.strip() for field in parsed_log]
        
        # Write the parsed log to the CSV file
        writer.writerow(parsed_log)
        
        # Print the parsed log
        print(parsed_log)
        
print("Done!")
