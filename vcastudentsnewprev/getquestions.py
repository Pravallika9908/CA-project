import pandas as pd

class GetQuestions:
   
    def get_questions(questionList):
        questionList = questionList+'.xlsx'
        try:
            df = pd.read_excel(questionList, header=None)
            # Assuming the data is in the first column of the Excel file
            df.columns = ['question','answer']
            questions_data = df.to_dict(orient='records')
            # print(questions_data)
            # questions = [{'question': question, 'answer': answer} for question, answer in questions_data.items()]
            return questions_data
        except Exception as e:
            print(f"Error reading Excel file: {e}")
            return []

