import openai
from ast import literal_eval

class Response:
  def __init__(self, _response):
    # data processing
    response = literal_eval(_response)
    self.input = response['input']
    self.question = response['question']
    self.answer = response['response']['answer']
    self.evidence = response['response']['evidences']

if __name__ == "__main__":
    # prompt engineering
    prompt = '''
            Here comes your prompts
    '''

    # retrieve responses
    openai.api_key = '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'
    completion = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {
            "role": "system",
            "content" : "You are a B2B legal AI service."},
            {"role": "user",
            "content": prompt}

        ]
    )

    _response = completion.choices[0].message.content # dict
    response = Response(_response)
    print(response)