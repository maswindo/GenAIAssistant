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
                f"Your response should not exceed 100 words.\n\nResume Text:\n{resume_text}"
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
        Simple Impact Agent - Suggests one impactful word change to improve phrasing.
        """
        prompt = {
            'system': "You are a resume impact expert skilled at improving the power of words and phrasing.",
            'user': (
                f"Analyze the resume and provide one concise suggestion to improve the phrasing of an achievement or responsibility. "
                f"Focus on replacing weak verbs, passive tone, or vague language. Your response should not exceed 100 words.\n\nResume Text:\n{resume_text}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["Impact"] = {"suggestion": suggestion}
        return suggestion

    def advanced_impact_agent(self, resume_text):
        """
        Advanced Impact Agent - Expands on word choice suggestions for stronger phrasing.
        """
        previous = self.simple_agent_storage.get("Impact", {}).get("suggestion", None)

        if not previous:
            # Direct analysis for impactful word choice
            prompt = {
                'system': "You are an expert in resume impact through stronger word choice.",
                'user': (
                    f"Analyze the resume and provide detailed feedback on how to strengthen the phrasing of achievements. "
                    f"Focus on replacing weak or vague words with powerful, action-oriented language.\n\nResume Text:\n{resume_text}"
                )
            }
        else:
            # Expand on the previous suggestion
            prompt = {
                'system': "You are an expert in enhancing resume phrasing for impact.",
                'user': (
                    f"The user received this impact suggestion: '{previous}'.\n\n"
                    f"Provide detailed guidance and examples of how to rephrase achievements with stronger verbs and more action-oriented language.\n\n"
                    f"Resume Text:\n{resume_text}"
                )
            }

        suggestion = self.interact_with_agent(prompt)
        return suggestion

    def visual_scan_agent(self, resume_text):
        """
        Simple Visual Scan Agent - Suggests quick visual improvements.
        """
        prompt = {
            'system': "You are an expert in improving resume formatting for quick visual scans.",
            'user': (
                f"Analyze the resume and provide the most important visual improvement. "
                f"Your response should not exceed 100 words.\n\nResume Text:\n{resume_text}"
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

    def branding_agent(self, resume_text):
        """
        Simple Branding Agent - Provides a unique branding improvement.
        """
        prompt = {
            'system': "You are a branding expert skilled at helping job seekers stand out.",
            'user': (
                f"Analyze the resume and provide one concise suggestion to improve the branding or professional uniqueness. "
                f"Your response should not exceed 100 words.\n\nResume Text:\n{resume_text}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["Branding"] = {"suggestion": suggestion}
        return suggestion

    def advanced_branding_agent(self, resume_text):
        """
        Advanced Branding Agent - Expands on the simple branding suggestion with detailed rationale.
        """
        previous = self.simple_agent_storage.get("Branding", {}).get("suggestion", None)

        if not previous:
            # If no previous suggestion exists, analyze directly
            prompt = {
                'system': "You are a branding expert skilled at helping job seekers stand out.",
                'user': (
                    f"Analyze the following resume and provide detailed feedback to improve branding or professional uniqueness. "
                    f"Suggest impactful changes and highlight what makes this resume memorable. "
                    f"Your response should include examples or actionable suggestions.\n\nResume Text:\n{resume_text}"
                )
            }
        else:
            # Expand on the previous suggestion
            prompt = {
                'system': "You are a branding expert skilled at enhancing professional uniqueness.",
                'user': (
                    f"The user previously received the following suggestion:\n"
                    f"Suggestion: {previous}\n\n"
                    f"Provide a detailed explanation of this suggestion, including specific changes or examples to make the resume's branding stand out.\n\n"
                    f"Resume Text:\n{resume_text}"
                )
            }

        return self.interact_with_agent(prompt)

    def quantification_agent(self, resume_text):
        """
        Simple Quantification Agent - Briefly suggests areas where metrics could be added.
        Avoids providing false or specific data.
        """
        prompt = {
            'system': "You are a resume expert skilled at identifying areas for measurable outcomes like numbers, percentages, or timeframes. "
                    "Do not invent or provide fake data.",
            'user': (
                f"Analyze the resume and provide a single, concise suggestion on where the user can add quantifiable outcomes "
                f"(e.g., numbers, percentages, or timeframes) to strengthen their achievements. "
                f"Your response should not exceed 100 words.\n\nResume Text:\n{resume_text}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["Quantification"] = {"suggestion": suggestion}
        return suggestion

    def advanced_quantification_agent(self, resume_text):
        """
        Advanced Quantification Agent - Provides detailed guidance on adding metrics.
        Expands upon the simple suggestion with actionable advice.
        """
        previous = self.simple_agent_storage.get("Quantification", {}).get("suggestion", None)

        if not previous:
            # If no simple suggestion exists, analyze directly
            prompt = {
                'system': "You are a resume expert skilled at identifying areas for measurable outcomes without falsifying information.",
                'user': (
                    f"Analyze the resume and suggest specific areas where quantifiable outcomes (e.g., team size, time saved, percentage growth) "
                    f"could strengthen achievements. Provide guidance but do not invent numbers.\n\nResume Text:\n{resume_text}"
                )
            }
        else:
            # Expand upon the simple suggestion
            prompt = {
                'system': "You are a resume expert skilled at helping users quantify their achievements responsibly.",
                'user': (
                    f"The user received this suggestion: '{previous}'.\n\n"
                    f"Provide detailed guidance on how to implement this suggestion. Suggest specific types of quantifiable outcomes "
                    f"relevant to their roles (e.g., timeframes, percentages, team sizes) without providing false numbers.\n\n"
                    f"Resume Text:\n{resume_text}"
                )
            }

        suggestion = self.interact_with_agent(prompt)
        return suggestion

    def ats_compatibility_agent(self, resume_text):
        """
        Simple ATS Compatibility Agent - Suggests a single improvement for ATS optimization.
        """
        prompt = {
            'system': "You are an expert in Applicant Tracking Systems (ATS) optimization for resumes.",
            'user': (
                f"Analyze the resume and provide one concise suggestion to improve its ATS compatibility. "
                f"Focus on formatting, keyword usage, or removing issues like images or unusual fonts. "
                f"Your response should not exceed 100 words.\n\nResume Text:\n{resume_text}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["ATS Compatibility"] = {"suggestion": suggestion}
        return suggestion

    def advanced_ats_compatibility_agent(self, resume_text):
        """
        Advanced ATS Compatibility Agent - Provides detailed feedback for ATS optimization.
        """
        previous = self.simple_agent_storage.get("ATS Compatibility", {}).get("suggestion", None)

        if not previous:
            # Analyze ATS compatibility directly
            prompt = {
                'system': "You are an expert in ATS optimization for resumes.",
                'user': (
                    f"Analyze the following resume and provide detailed feedback on improving ATS compatibility. "
                    f"Include suggestions for keywords, formatting, section headings, or fixing ATS-blocking issues.\n\nResume Text:\n{resume_text}"
                )
            }
        else:
            # Expand on the previous simple suggestion
            prompt = {
                'system': "You are an expert in ATS optimization for resumes.",
                'user': (
                    f"The user received this ATS suggestion: '{previous}'.\n\n"
                    f"Provide detailed feedback and specific steps to implement this suggestion, including formatting changes, keyword additions, or common ATS issues to avoid.\n\n"
                    f"Resume Text:\n{resume_text}"
                )
            }

        suggestion = self.interact_with_agent(prompt)
        return suggestion

    def action_verb_agent(self, resume_text):
        """
        Simple Action Verb Agent - Suggests a stronger action verb to replace a weak or generic verb.
        """
        prompt = {
            'system': "You are a resume expert skilled at enhancing achievements by replacing weak or generic verbs "
                    "with strong, action-oriented language.",
            'user': (
                f"Analyze the resume and provide one concise suggestion to replace a weak or generic verb "
                f"with a stronger action-oriented verb. Your suggestion should not exceed 100 words.\n\nResume Text:\n{resume_text}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["Action Verb"] = {"suggestion": suggestion}
        return suggestion

    def advanced_action_verb_agent(self, resume_text):
        """
        Advanced Action Verb Agent - Provides detailed feedback to replace weak verbs and improve phrasing.
        """
        previous = self.simple_agent_storage.get("Action Verb", {}).get("suggestion", None)

        if not previous:
            # If no simple suggestion exists, analyze directly
            prompt = {
                'system': "You are an expert in resume writing, specializing in improving phrasing with strong action verbs.",
                'user': (
                    f"Analyze the resume and identify multiple weak or generic verbs. "
                    f"Provide detailed suggestions to replace them with stronger, action-oriented alternatives. "
                    f"Ensure the phrasing remains professional and impactful.\n\nResume Text:\n{resume_text}"
                )
            }
        else:
            # Expand upon the previous simple suggestion
            prompt = {
                'system': "You are an expert in improving resumes with strong, impactful action verbs.",
                'user': (
                    f"The user received this suggestion: '{previous}'.\n\n"
                    f"Provide detailed feedback to expand on this suggestion. Identify other verbs in the resume that could "
                    f"be improved and suggest stronger alternatives. Keep the phrasing professional and impactful.\n\n"
                    f"Resume Text:\n{resume_text}"
                )
            }

        suggestion = self.interact_with_agent(prompt)
        return suggestion

    def achievements_highlight_agent(self, resume_text):
        """
        Simple Achievements Highlight Agent - Highlights one key achievement and provides a suggestion
        to align it with the inferred scope or intended goal of the resume.
        """
        prompt = {
            'system': "You are a career coach specializing in resume optimization. Your task is to infer the intended career goal "
                    "from the resume and help the user highlight their most impactful achievements.",
            'user': (
                f"Analyze the following resume and infer the career goal or scope based on the content (e.g., software development, data analysis). "
                f"Identify one key achievement that aligns with the inferred goal. Explain why this achievement is valuable and provide one suggestion "
                f"to emphasize or position it better. Your response must not exceed 100 words.\n\nResume Text:\n{resume_text}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["Achievements Highlight"] = {"suggestion": suggestion}
        return suggestion



    def advanced_achievements_highlight_agent(self, resume_text):
        """
        Advanced Achievements Highlight Agent - Analyzes the resume to identify multiple key achievements,
        infer the intended career goal, and provide detailed suggestions for emphasizing those achievements.
        """
        previous = self.simple_agent_storage.get("Achievements Highlight", {}).get("suggestion", None)

        if not previous:
            # Analyze holistically if no simple suggestion exists
            prompt = {
                'system': "You are a career advisor specializing in resume optimization. Your task is to infer the user's career goal "
                        "from the resume and help highlight achievements that align with this goal.",
                'user': (
                    f"Analyze the following resume to infer the intended career goal (e.g., data science, software engineering). "
                    f"Identify 2-3 key achievements that are most impactful and relevant to the inferred goal. "
                    f"Provide detailed suggestions on how to emphasize these achievements, including phrasing improvements, placement, or value alignment.\n\n"
                    f"Resume Text:\n{resume_text}"
                )
            }
        else:
            # Expand upon the simple suggestion
            prompt = {
                'system': "You are a career advisor specializing in resume optimization.",
                'user': (
                    f"The user previously received this achievement highlight suggestion: '{previous}'.\n\n"
                    f"Build upon this by identifying other key achievements that align with the inferred career goal. "
                    f"Provide detailed strategies for emphasizing these achievements to make the resume more impactful and relevant.\n\n"
                    f"Resume Text:\n{resume_text}"
                )
            }

        suggestion = self.interact_with_agent(prompt)
        return suggestion


    def tailoring_agent(self, resume_text, job_description):
        """
        Tailoring Agent - Analyzes resume and job description for alignment.
        """
        prompt = {
            'system': "You are an expert in aligning resumes to job descriptions without falsifying information.",
            'user': (
                f"Compare the following resume with the provided job description. "
                f"Suggest clear adjustments to the resume to better fit the job. "
                f"Focus on wording, structure, and highlighting relevant skills. "
                f"Your suggestions must not exceed 50 words.\n\nResume Text:\n{resume_text}\n\nJob Description:\n{job_description}"
            )
        }
        suggestion = self.interact_with_agent(prompt)
        self.simple_agent_storage["Tailoring"] = {"suggestion": suggestion}
        return suggestion


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
