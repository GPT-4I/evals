def battle(system_input1, user_input1, completion1, system_input2, user_input2, completion2):

    # Paths. Assuming this notebook is in evals/evals

    battle_path = os.path.join(os.getcwd(), "registry", "data", "battle")
    os.makedirs(battle_path, exist_ok=True)
    battle_path = os.path.join(battle_path, "samples.jsonl")

    # Data

    input1 = ([{"role":"system","content":system_input1},{"role":"user","content":user_input1}])
    input2 = ([{"role":"system","content":system_input2},{"role":"user","content":user_input2}])

    dataset = [{"input1": input1, "completion1": completion1, "input2": input2, "completion2":completion2}]
 

    df = pd.DataFrame(dataset)
    df.to_json(battle_path, orient="records", lines=True)
    
    import subprocess

    command = "oaieval gpt-3.5-turbo battle --record_path /workspaces/evals/evallogs/logs"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Command failed with error {process.returncode}: {stderr.decode()}")
    else:
        print(f"Command succeeded with output: {stdout.decode()}")

    
    events = "/workspaces/evals/evallogs/logs"
    record_path = os.path.join("/workspaces/evals/evallogs/eval")
    with open(events, "r") as f:
        events_df = pd.read_json(f, lines=True)

    os.makedirs(record_path, exist_ok=True)
    events_df.to_json(os.path.join(record_path, "events"), lines=True, orient="records")
    events_df["data"].to_json(os.path.join(record_path, "data"), lines=True, orient="records")
    data_df = pd.read_json(os.path.join(record_path, "data"), lines=True)
    for row in data_df[0]:
        s = str(row)
        s = s.replace("[","",-1)
        s = s.replace("]","",-1)
        if s.startswith("{'choice':"):
            s = s.split("'")[3]
            choice = s
        if s.startswith("{'prompt': {'role': 'user', 'content': 'You are comparing two responses to the following two instructions."):
            #s = s.split("\\n\\nInstruction 1\\n",)[1]
            #instruction1 = s.split("\\n\\nResponse 1\\n")[0].replace("\\'","'").replace("\\n","\n")
            #s = s.split("\\nResponse 1\\n",)[1]
            #response1 = s.split("\\n\\nInstruction 2\\n")[0].replace("\\'","'").replace("\\n","\n")
            #s = s.split("\\n\\nInstruction 2\\n",)[1]
            #instruction2 = s.split("\\n\\nResponse 2\\n")[0].replace("\\'","'").replace("\\n","\n")
            #s = s.split("\\nResponse 2\\n",)[1]
            #response2 = s.split("\\n\\n\\nWhich of the following responses is better?")[0].replace("\\'","'").replace("\\n","\n")
            sampled = s.split("\\n\\nReasoning:\'}, \'sampled\': ")[1].replace("\\'","'").replace("\\n","\n")
    
    #content = data["choices"]["message"]["content"]
    #choice = content.split("\\n")[-1]
    data = {'Choice': choice, 'Instruction1': user_input1, 'Response1': completion1, 'Instruction2': user_input2, 'Response2': completion2, 'Sampled': sampled}
    
    return data


def test_match(test_dataset):
    data = []
    for t in range(0,len(test_dataset)):
        data.append({"input":[{"role":"system","content":""},{"role":"user","content":test_dataset[t][0]}], "ideal":test_dataset[t][2]})
    df = pd.DataFrame(data)

    # Paths. Assuming this notebook is in evals/evals

    test_match_path = os.path.join(os.getcwd(), "registry", "data", "match")
    os.makedirs(test_match_path, exist_ok=True)
    test_match_path = os.path.join(test_match_path, "samples.jsonl")

    df.to_json(test_match_path, orient="records", lines=True)
    
    import subprocess

    command = "oaieval gpt-3.5-turbo match --record_path /workspaces/evals/evallogs/logs"
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    stdout, stderr = process.communicate()

    if process.returncode != 0:
        print(f"Command failed with error {process.returncode}: {stderr.decode()}")
    else:
        print(f"Command succeeded with output: {stdout.decode()}")

    
    events = "/workspaces/evals/evallogs/logs"
    record_path = os.path.join("/workspaces/evals/evallogs/eval")
    with open(events, "r") as f:
        events_df = pd.read_json(f, lines=True)
    
    os.makedirs(record_path, exist_ok=True)
    events_df.to_json(os.path.join(record_path, "events"), lines=True, orient="records")
    events_df["data"].to_json(os.path.join(record_path, "data"), lines=True, orient="records")
    data_df = pd.read_json(os.path.join(record_path, "data"), lines=True)
    
    return data_df

def content_to_list(content, dataset):
    dataset_df = pd.DataFrame(dataset)
    return dataset[dataset_df[0].to_list().index(content)]

def append_response(content, response, dataset):
    dataset_df = pd.DataFrame(dataset)
    index = dataset_df[0].to_list().index(content)
    dataset[index][2].append(response)
    return len(dataset[index][2])