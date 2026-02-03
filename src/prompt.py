class Prompt:
    @staticmethod
    def prompt1(ID=0):
        if ID == 0:
            # Full Explanation (most detailed)
            prompt_text = """Your task: Read the complete video transcript below and create a detailed, informative summary that explains the topic thoroughly in plain text.

CRITICAL INSTRUCTION: You MUST analyze the full transcript and create a comprehensive summary that explains HOW things work, not just WHAT they are. Include important details, sequences, rules, and processes mentioned in the video.

OUTPUT FORMAT RULES:
- Use PLAIN TEXT ONLY - absolutely no Markdown formatting
- No hashtags (#, ##), bold (**), asterisks, dashes, or bullet symbols
- Write in natural paragraphs with clear breaks between sections
- Use complete sentences that flow naturally
- Length should be sufficient to fully explain the topic (aim for thorough understanding, not brevity)

CONTENT REQUIREMENTS:
- Explain concepts step-by-step as presented in the video
- Describe how processes work, what is required, and how things are set up
- Include specific details, rules, sequences, or procedures mentioned
- Maintain logical flow from introduction through explanation to conclusion
- Use clear, simple English that anyone can understand
- Focus on being informative and educational

WRITING STYLE:
- Start by explaining what the video is about
- Then describe the main concepts or processes in detail
- Explain how things work, what steps are involved, what is needed
- Include important specifics like rules, requirements, or sequences
- Conclude with final points or summary of the overall topic
- Write as if teaching someone who knows nothing about the subject

IMPORTANT GUIDELINES:
- Base everything ONLY on what is actually said in the transcript
- Do NOT invent or assume information not present
- Do NOT oversimplify - include necessary details for understanding
- Do NOT use abstract or vague language
- Prefer clarity and completeness over brevity
- Think of this as a "how it works" or "rules explanation" guide

Example flow (plain text style):
"This video explains [topic]. To begin with, [first concept]. The process involves [details]. Additionally, [more information]. Finally, [conclusion]."

VIDEO TRANSCRIPT TO SUMMARIZE:
"""
        
        elif ID == "detailed":
            # Detailed Summary (balanced - medium length)
            prompt_text = """Your task: Read the video transcript below and create a focused summary that explains the core topic clearly in plain text.

CRITICAL INSTRUCTION: Analyze the transcript and produce a medium-length summary (around 150-200 words) that covers the main topic, core process, and key points. Focus on essentials - avoid exhaustive details, edge cases, or rare scenarios.

OUTPUT FORMAT RULES:
- Use PLAIN TEXT ONLY - no Markdown formatting
- No hashtags, bold, asterisks, dashes, or bullet symbols
- Write in short, clear paragraphs
- Use complete, flowing sentences
- Target length: 150-200 words

CONTENT REQUIREMENTS:
- Opening: explain what the video is about
- Core setup: describe main requirements or setup (if applicable)
- Main process: explain the primary flow, rules, or steps
- Focus on the main points that help viewers understand how it works
- Use simple, clear, educational language

WHAT TO INCLUDE:
- Essential information to understand the topic
- Main rules or process flow
- Core requirements or setup steps
- Key definitions if needed

WHAT TO EXCLUDE:
- Exhaustive lists of edge cases or fouls
- Rare or technical scenarios
- Tie-breaker or exceptional end-game details
- Minor variations or uncommon situations
- Overly detailed step-by-step breakdowns

WRITING STYLE:
- Clear and informative without being exhaustive
- Explain enough to understand how it works
- Keep paragraphs short and focused
- Educational but concise
- Think: "Now I understand the main idea" not "I know every detail"

IMPORTANT GUIDELINES:
- Base on actual transcript content only
- Do NOT invent information
- Keep it focused on core concepts
- Prioritize clarity and usefulness
- Aim for practical understanding

Example reference style:
"This video explains [topic and purpose]. To start, you need [core items]. The main process involves [key steps]. [Core rules]. [Important point]. This gives viewers [outcome]."

VIDEO TRANSCRIPT TO SUMMARIZE:
"""
        
        elif ID == "short":
            # Short Summary (quick overview)
            prompt_text = """Your task: Read the video transcript below and create a brief, crisp summary in plain text.

CRITICAL INSTRUCTION: Compress the main points into a quick overview that explains what the video is about and 2-3 key takeaways. Keep it short and skimmable.

OUTPUT FORMAT RULES:
- Use PLAIN TEXT ONLY - no Markdown formatting
- No bullet points, hashtags, bold, or special symbols
- Write in natural, flowing sentences
- Maximum 4-6 sentences total
- Keep it crisp and easy to skim

CONTENT REQUIREMENTS:
- First sentence: what the video is about
- Next 2-3 sentences: main points or key information
- Final sentence: conclusion or outcome
- Use simple, clear language
- Focus on the essentials only

WRITING STYLE:
- Straightforward and direct
- No unnecessary details
- Easy to read quickly
- User-friendly and accessible

IMPORTANT GUIDELINES:
- Base on actual transcript content only
- Do NOT add information not present
- Keep it very concise
- Prioritize clarity over completeness
- Think "quick overview" not "deep dive"

Example flow:
"This video explains [topic]. It covers [key point 1] and [key point 2]. The video also discusses [key point 3]. [Brief conclusion]."

VIDEO TRANSCRIPT TO SUMMARIZE:
"""

        elif ID == "timestamp":
            prompt_text = """
            Generate timestamps for main chapter/topics in a YouTube video transcript.
            Given text segments with their time, generate timestamps for main topics discussed in the video. Format timestamps as hh:mm:ss and provide clear and concise topic titles.  
           
            Instructions:
            1. List only topic titles and timestamps.
            2. Do not explain the titles.
            3. Include clickable URLs.
            4. Provide output in Markdown format.

            Markdown for output:
            1. [hh:mm:ss](%VIDEO_URL?t=seconds) %TOPIC TITLE 1%
            2. [hh:mm:ss](%VIDEO_URL?t=seconds) %TOPIC TITLE 2%
            - and so on

            Markdown Example:
            1. [00:05:23](https://youtu.be/hCaXor?t=323) Introduction
            2. [00:10:45](https://youtu.be/hCaXor?t=645) Main Topic 1
            3. [00:25:17](https://youtu.be/hCaXor?t=1517) Main Topic 2
            - and so on

            The %VIDEO_URL% (YouTube video link) and transcript are provided below :
            """
            
        elif ID == "transcript":
            prompt_text = ""

        else:
            prompt_text = ""

        return prompt_text
