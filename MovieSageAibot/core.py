# MovieSage AI bot
# 1 take a raw para about a movie
# 2 Extract important sturtured info
# 3 Generate a clean summary
# 4 Returns it into JSON Format

from dotenv import load_dotenv

load_dotenv()
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_mistralai import ChatMistralAI
from pydantic import BaseModel, Field

class MovieInfo(BaseModel):
    title: str = Field(description="The title of the movie")
    genre: str = Field(description="The genre of the movie")
    director: str = Field(description="The director of the movie")
    writers: list = Field(description="The writers of the movie")
    producers: list = Field(description="The producers of the movie")
    cast: list = Field(description="The cast of the movie")
    release_year: int = Field(description="The release year of the movie")
    runtime: int = Field(description="The runtime of the movie in minutes")
    language: str = Field(description="The language of the movie")
    country: str = Field(description="The country of origin of the movie")
    plot_summary: str = Field(description="A concise summary of the movie's plot")
    main_characters: list = Field(description="The main characters in the movie")
    themes: list = Field(description="The themes explored in the movie")
    notable_facts: list = Field(description="Notable facts about the movie")
    awards: list = Field(description="Awards won by the movie")
    box_office: str = Field(description="Box office performance of the movie")
    rating: float = Field(description="The rating of the movie")
    keywords: list = Field(description="Keywords associated with the movie")

parser = PydanticOutputParser(pydantic_object=MovieInfo)
model = ChatMistralAI(model="mistral-small-2603")

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
You are MovieSage AI, an expert movie analyst and information extraction assistant.

```
    Your responsibilities:

    1. Carefully read and understand the entire movie description.
    2. Extract all important movie-related information.
    3. Generate a concise and engaging plot summary.
    4. Identify key characters, themes, and notable facts.
    5. Extract factual information only from the provided text.
    6. If information is not available, return null.
    7. Never hallucinate or invent details.
    8. Return ONLY valid JSON.
    9. Do not include markdown, explanations, comments, or additional text.

    Extract the following fields:

    - title
    - genre
    - director
    - writers
    - producers
    - cast
    - release_year
    - runtime
    - language
    - country
    - plot_summary
    - main_characters
    - themes
    - notable_facts
    - awards
    - box_office
    - rating
    - keywords

    
    """,
        ),
        (
            "human",
            """
    Analyze the following movie description and extract all relevant information.

    Movie Description:
    {movie_description}
    """,
        ),
    ]
)

para = input("give your paragraph")
final_prompt = prompt.invoke({"movie_description": para})

res = model.invoke(final_prompt)
print(res.content)
