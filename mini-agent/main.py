from flask import Flask, request, jsonify
from agents.Intervention_agent import InterventionAgent


app = Flask(__name__)
agent = InterventionAgent(agent_name="InterventionAgent", task_input="")

def receive_trigger(agent, trigger_data):
    event_type = trigger_data.get('event_type')
    if event_type == 'lasting_cough_detected':
        agent.task_input = ("The user has been coughing for a significant period. "
                            "Talk to him to stimulate his memory of past actions that led to his current cough and give him corresponding suggestions.")
        return agent.run()
    elif event_type == 'throat_clear_detected':
        agent.task_input = ("The user has been clearing their throat frequently. "
                            "Talk to him to stimulate his memory of past actions that led to his current throat clearing and give him corresponding suggestions.")
        return agent.run()
    else:
        return "Unknown event type received." 
    
@app.route('/trigger', methods=['POST'])
def trigger():
    trigger_data = request.json
    response = receive_trigger(agent, trigger_data)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
