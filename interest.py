import os
from dotenv import load_dotenv
import streamlit as st
from langchain.llms import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.schema import (
    AIMessage,
    HumanMessage,
    SystemMessage
)
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory
from langchain.utilities import WikipediaAPIWrapper

load_dotenv()

st.title("Claim Interest Scoring")
claim = st.text_input("Write a claim here")

chat = ChatOpenAI(model_name="gpt-4", temperature=0.3)

system_message_prompt = SystemMessagePromptTemplate.from_template("You are a helpful assistant that works for a news company.")
explanation = """
Now, I will describe the criteria for evaluating the interest score of a claim. Each criterion should be scored between 1 and 10. Do not explain your scores, just provide the scores for each criterion. It should be formatted similarly to the example output.
CRITERION:
1. **Relevance:** A claim should be evaluated based on its relevance to the news article or topic. If the claim is highly relevant to the subject matter, it should be assigned a higher score. For instance, if the article is about geopolitical tensions between Russia and Ukraine, then the given claim is very relevant.

2. **Significance:** Evaluate how significant the claim is. If the claim could have profound implications on the global stage, then it should be scored higher. For example, if the claim is proven true, it could lead to significant geopolitical shifts and potential escalations.

3. **Controversy:** Consider the level of controversy associated with the claim. If the claim is likely to spark debate or disagreement, it could be seen as more interesting. In this case, a claim of an unprovoked offensive is certainly controversial.

4. **Uniqueness:** If the claim is something that hasn't been heard before or is a new development in a story, it could be assigned a higher score for interest.

5. **Reliability:** The source of the claim should also be considered. If the claim is coming from a highly reliable source, it could be deemed more interesting, as it's more likely to be true.

6. **Timeliness:** Current or recent claims tend to be more interesting because they reflect the latest developments. If a claim is about an event that happened years ago and isn't connected to current events, it may be less interesting.

Now, I will provide an example of an input claim and the output scores for each criterion.
INPUT CLAIM: "Russia has launched an unprovoked offensive against Ukraine."
EXPECTED OUTPUT:
Relevance: 9
Significance: 9
Controversy: 9
Uniqueness: 7
Reliability: 5
Timeliness: 9
"""
human_message_prompt_1 = HumanMessagePromptTemplate.from_template(explanation)
human_message_prompt_2 = HumanMessagePromptTemplate.from_template("Using the previous information, please evaluate the interest score of the following claim: \"{claim}\". Here is some Wikipedia research to help you: {wikipedia_research}")

chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt_1, human_message_prompt_2])


wiki = WikipediaAPIWrapper()


if claim:
    wikipedia_research = wiki.run(claim)
    response = chat(chat_prompt.format_prompt(claim=claim, wikipedia_research=wikipedia_research).to_messages())
    output = response.content
    st.write(output)

    with st.expander("Wikipedia Research"):
        st.info(wikipedia_research)
