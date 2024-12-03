from langchain.schema import HumanMessage, SystemMessage
import logging

logging.basicConfig(level=logging.DEBUG)

class AgentManager:
    def __init__(self, chat_client):
        """
        Initialize the AgentManager with a GPT chat client.
        """
        self.chat = chat_client
        self.simple_agent_storage = {}  # To store results of simple agents

    def clarity_agent(self, resume_text):
        """
        Simple Clarity Agent - Provides a single suggestion.
        """
        prompt = {
            'system': "You are an expert in enhancing resume clarity.",
            'user': (
                f"Analyze the following resume and provide only one concise, impactful improvement to enhance readability. "
                f"Your response should not exceed 30 words.\n\nResume Text:\n{resume_text}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["Clarity"] = {"suggestion": suggestion}
        return suggestion

    def advanced_clarity_agent(self, resume_text):
        """
        Advanced Clarity Agent - Builds upon the simple agent's suggestion.
        """
        previous = self.simple_agent_storage.get("Clarity", {}).get("suggestion", None)

        if not previous:
            # If no previous suggestion, analyze the resume directly
            prompt = {
                'system': "You are an expert in resume clarity and structure.",
                'user': (
                    f"Analyze the following resume and provide detailed feedback to improve clarity. "
                    f"Include specific examples of formatting or content changes to make the resume more readable and professional.\n\nResume Text:\n{resume_text}"
                )
            }
            return self.interact_with_agent(prompt)

        # If a previous suggestion exists, expand upon it
        prompt = {
            'system': "You are an expert in resume clarity and structure.",
            'user': (
                f"The user previously received the following suggestion:\n"
                f"Suggestion: {previous}\n\n"
                "Provide a detailed rationale for this suggestion. Include specific examples of formatting or content improvements. "
                "Your response should be clear and actionable.\n\nResume Text:\n{resume_text}"
            )
        }
        return self.interact_with_agent(prompt)

    def impact_agent(self, resume_text):
        """
        Simple Impact Agent - Identifies impactful changes.
        """
        prompt = {
            'system': "You are a resume impact expert skilled at emphasizing achievements and quantifying results.",
            'user': (
                f"Review the resume and provide the most impactful change to improve the impact of achievements. "
                f"Your response should not exceed 30 words.\n\nResume Text:\n{resume_text}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["Impact"] = {"suggestion": suggestion}
        return suggestion

    def advanced_impact_agent(self, resume_text):
        """
        Advanced Impact Agent - Expands on the simple agent's suggestion.
        """
        previous = self.simple_agent_storage.get("Impact", {}).get("suggestion", None)

        if not previous:
            # If no previous suggestion, analyze the resume directly
            prompt = {
                'system': "You are an expert in enhancing the impact of achievements on resumes.",
                'user': (
                    f"Analyze the following resume and provide detailed feedback on how to emphasize achievements. "
                    f"Include examples of rephrasing or quantifying accomplishments to maximize their impact.\n\nResume Text:\n{resume_text}"
                )
            }
            return self.interact_with_agent(prompt)

        # If a previous suggestion exists, expand upon it
        prompt = {
            'system': "You are an expert in enhancing the impact of achievements on resumes.",
            'user': (
                f"The user previously received the following suggestion:\n"
                f"Suggestion: {previous}\n\n"
                "Provide a detailed rationale for this suggestion. Include examples of how to rephrase or quantify "
                "achievements to maximize their impact.\n\nResume Text:\n{resume_text}"
            )
        }
        return self.interact_with_agent(prompt)

    def visual_scan_agent(self, resume_text):
        """
        Simple Visual Scan Agent - Suggests quick visual improvements.
        """
        prompt = {
            'system': "You are an expert in improving resume formatting for quick visual scans.",
            'user': (
                f"Analyze the resume and provide the most important visual improvement. "
                f"Your response should not exceed 30 words.\n\nResume Text:\n{resume_text}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["Visual Scan"] = {"suggestion": suggestion}
        return suggestion

    def advanced_visual_scan_agent(self, resume_text):
        """
        Advanced Visual Scan Agent - Builds on the simple agent's suggestion.
        """
        previous = self.simple_agent_storage.get("Visual Scan", {}).get("suggestion", None)

        if not previous:
            # If no previous suggestion, analyze the resume directly
            prompt = {
                'system': "You are an expert in improving resume visual presentation.",
                'user': (
                    f"Analyze the following resume and provide detailed feedback on visual improvements. "
                    f"Include examples of better layout, font choices, and formatting for improved readability and recruiter engagement.\n\nResume Text:\n{resume_text}"
                )
            }
            return self.interact_with_agent(prompt)

        # If a previous suggestion exists, expand upon it
        prompt = {
            'system': "You are an expert in improving resume visual presentation.",
            'user': (
                f"The user previously received the following suggestion:\n"
                f"Suggestion: {previous}\n\n"
                "Provide a detailed explanation of why this visual change is critical. Include examples of improved "
                "layout and formatting for better recruiter engagement.\n\nResume Text:\n{resume_text}"
            )
        }
        return self.interact_with_agent(prompt)

    def interact_with_agent(self, agent_prompt):
        """
        Send prompts to GPT and return the response, focusing on the suggestion only.
        """
        try:
            messages = [
                SystemMessage(content=agent_prompt['system']),
                HumanMessage(content=agent_prompt['user'])
            ]

            response = self.chat(messages)
            content = response.content.strip()

            logging.debug(f"Agent Response: {content}")
            # Return the content directly since we're only expecting a suggestion or detailed feedback
            return content
        except Exception as e:
            logging.error(f"Error interacting with agent: {e}")
            return f"Error interacting with agent: {e}"
