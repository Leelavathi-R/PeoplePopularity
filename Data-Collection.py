from pytrends.request import TrendReq
import wikipediaapi
import pandas as pd
import requests
import json

def getGoogleTrendsData(persons):
    pytrends = TrendReq(hl='en', tz=360)
    pytrends.build_payload(persons, timeframe='2016-01-01 2020-12-31')
    data = pytrends.interest_over_time()
    print(data)
    data.to_csv('./combined_data.csv')

def getWikiPageViews(persons):
    page_views = []
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
    for name in persons:
        title = name.replace(" ","_")
        url = f'https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/{title}/monthly/20160101/20201231'
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)
        print(data)
        for item in data['items']:
            print(title, item['views'],item['timestamp'],sep='\t')
            page_views.append(item['views'])
    print(page_views)
    return page_views

def getWikiEdits(persons,years):
    edits = []
    for name in persons:
        title = name.replace(" ","_")
        monthly_edits = {'2016-01': 0, '2016-02': 0, '2016-03': 0, '2016-04': 0, '2016-05': 0, '2016-06': 0, '2016-07': 0, '2016-08': 0, '2016-09': 0, '2016-10': 0, '2016-11': 0, '2016-12': 0, '2017-01': 0, '2017-02': 0, '2017-03': 0, '2017-04': 0, '2017-05': 0, '2017-06': 0, '2017-07': 0, '2017-08': 0, '2017-09': 0, '2017-10': 0, '2017-11': 0, '2017-12': 0, '2018-01':0,'2018-02': 0, '2018-03': 0, '2018-04': 0, '2018-05': 0, '2018-06': 0, '2018-07': 0, '2018-08': 0, '2018-09': 0,'2018-10': 0, '2018-11': 0, '2018-12': 0, '2019-01': 0, '2019-02': 0, '2019-03': 0, '2019-04': 0, '2019-05': 0, '2019-06': 0, '2019-07': 0, '2019-08': 0, '2019-09': 0, '2019-10': 0, '2019-11': 0, '2019-12': 0, '2020-01': 0, '2020-02': 0,'2020-03': 0, '2020-04': 0, '2020-05': 0, '2020-06': 0, '2020-07': 0, '2020-08': 0, '2020-09': 0, '2020-10': 0, '2020-11': 0, '2020-12': 0}
        for year in years:
            start_date = year+"-01-01T00:00:00Z"
            end_date = year+"-12-31T23:59:59Z"
            print(start_date,end_date)
            api_url = f'https://en.wikipedia.org/w/api.php?action=query&format=json&prop=revisions&titles={title}&rvlimit=500&rvprop=timestamp&rvdir=newer&rvstart={start_date}&rvend={end_date}'
            response = requests.get(api_url)
            data = response.json()
            #with open('./edit.json', 'r') as json_file:
            #    data = json.load(json_file)
            PAGE_ID = list(data["query"]["pages"].keys())[0]
            revisions = data["query"]["pages"][PAGE_ID]["revisions"]
            print(revisions)
            print(len(revisions))
            for edit in revisions:
                month = edit['timestamp'].split('-')
                monthly_edits[(month[0]+'-'+month[1])] += 1
        edits.extend(list(monthly_edits.values()))
    print(edits)
    return edits

def calculateMonthlyPopularity(file,nationality):
    #removing unwanted column
    person_df = pd.read_csv(file)
    if 'isPartial' in person_df:
        del person_df['isPartial']
        print(person_df)

    #aggregating monthly popularity
    person_df['date'] = pd.to_datetime(person_df['date'])
    person_df.set_index('date',inplace=True)
    person_monthly_df = person_df.resample('M').mean()
    person_monthly_df.reset_index(inplace=True)
    print(person_monthly_df)

    #changing from wide to long format
    person_long_df = pd.melt(person_monthly_df, id_vars='date', var_name='name', value_name='relative_popularity')
    person_long_df['nationality'] = person_long_df['name'].map(nationality)
    print(person_long_df)
    return person_long_df

def dataIntegration():
    profession = {'Sundar Pichai':'IT','A. R. Rahman':'Music','Narendra Modi':'Politics','MS Dhoni':'Sports','Satya Nadella':'IT','B. R. Ambedkar':'Politics','Rajinikanth':'Cinema','Shah Rukh Khan':'Cinema','Sachin Tendulkar':'Sports','Srinivasa Ramanujan':'Mathematics',
    'Barack Obama':'Politics','Bill Gates':'IT','Taylor Swift':'Music','Elon Musk':'Entrepreneur','Martin Luther King Jr.':'Activism','Indira Gandhi':'Politics','Mohanlal':'Cinema','Vijay Mallya':'Entrepreneur','Rohit Sharma':'Sports','Mamata Banerjee':'Politics','Johnny Depp':'Cinema','Britney Spears':'Cinema','Lady Gaga':'Music','Mark Zuckerberg':'Entrepreneur','Michelle Obama':'Politics',
    'Deepika Padukone':'Cinema','Aishwarya Rai Bachchan':'Cinema','Shreya Ghoshal':'Music','Kiren Rijiju':'Politics','Priyanka Chopra':'Cinema','Vladimir Putin':'Politics','Steve Jobs':'Entrepreneur','Nelson Mandela':'Politics','Albert Einstein':'Science','Emma Watson':'Cinema',
    'Cristiano Ronaldo':'Sports','William Shakespeare':'Poet','Leonardo da Vinci':'Science','Michael Jackson':'Music','Beyoncé':'Music','Dwayne Johnson':'Sports','Justin Bieber':'Music','Lionel Messi':'Sports','Rihanna':'Entrepreneur','Selena Gomez':'Cinema','Anushka Shetty':'Cinema','Kamal Haasan':'Cinema','Mary Kom':'Sports','Akshay Kumar':'Cinema','Amitabh Bachchan':'Cinema'}
    df1 = pd.read_csv('./person_data/1-5people.csv')
    df2 = pd.read_csv('./person_data/6-10people.csv')
    df3 = pd.read_csv('./person_data/11-15people.csv')
    df4 = pd.read_csv('./person_data/16-20people.csv')
    df5 = pd.read_csv('./person_data/21-25people.csv')
    df6 = pd.read_csv('./person_data/26-30people.csv')
    df7 = pd.read_csv('./person_data/31-35people.csv')
    df8 = pd.read_csv('./person_data/36-40people.csv')
    df9 = pd.read_csv('./person_data/41-45people.csv')
    df10 = pd.read_csv('./person_data/46-50people.csv')
    integrated_df = pd.concat([df1,df2,df3,df4,df5,df6,df7,df8,df9,df10], axis=0)
   
    avg_page_views = integrated_df['page_views'].mean()
    avg_rel_popularity = integrated_df['relative_popularity'].mean()
    integrated_df['popular'] = integrated_df.apply(lambda row: 'yes' if row['page_views'] > avg_page_views or row['relative_popularity'] > avg_rel_popularity else 'no',axis=1)
    integrated_df.insert(len(integrated_df.columns) - 1, 'profession', integrated_df['name'].map(profession))

    print(integrated_df)
    integrated_df.to_csv('./people-popularity.csv',index=False)

if __name__ == '__main__':
    #Defining persons to collect information from Google Trends
    persons = ['Anushka Shetty','Kamal Haasan','Mary Kom','Akshay Kumar','Amitabh Bachchan']
    nationality = {'Vladimir Putin':'RU-SP',',Steve Jobs':'US-CA','Nelson Mandela':'SA-CP','Albert Einstein':'DE-BW','Emma Watson':'UK-LDN'}
    year = ['2016','2017','2018','2019','2020']
    getGoogleTrendsData(persons)
    people_df = calculateMonthlyPopularity('./combined_data.csv',nationality)
    page_views = getWikiPageViews(persons)
    people_df['page_views'] = page_views
    edits = getWikiEdits(persons,year)
    people_df['edits'] = edits
    print(people_df)
    people_df.to_csv('./person_data/46-50people.csv',index=False)
    #dataIntegration()

# ----------- 50 people --------
#collected_persons1 = ['Sundar Pichai','A. R. Rahman','Narendra Modi','MS Dhoni','Satya Nadella']
#collected_persons2 = ['B. R. Ambedkar','Rajinikanth','Shah Rukh Khan','Sachin Tendulkar','Srinivasa Ramanujan']
#nationality = {'B. R. Ambedkar':'IN-MH','Rajinikanth':'IN-KA','Shah Rukh Khan':'IN-DL','Sachin Tendulkar':'IN-MH','Srinivasa Ramanujan':'IN-TN'}
#collected_persons3 = ['Barack Obama','Bill Gates','Taylor Swift','Elon Musk','Martin Luther King Jr.']
#nationality = {'Barack Obama':'US-HI','Bill Gates':'US-WA','Taylor Swift':'US-PA','Elon Musk':'SA','Martin Luther King Jr.':'US-GA'}
#collected_persons4 = ['Indira Gandhi','Mohanlal','Vijay Mallya','Rohit Sharma','Mamata Banerjee']
#nationality = {'Indira Gandhi':'IN-UP','Mohanlal':'IN-KL','Vijay Mallya':'IN-KA','Rohit Sharma':'IN-MH','Mamata Banerjee':'IN-WB'}
#persons = ['Johnny Depp','Britney Spears','Lady Gaga','Mark Zuckerberg','Michelle Obama']
#nationality = {'Johnny Depp':'US-KY','Britney Spears':'US-MS','Lady Gaga':'US-NY','Mark Zuckerberg':'US-NY','Michelle Obama':'US-IL'}
#persons = ['Deepika Padukone','Aishwarya Rai Bachchan','Shreya Ghoshal','Kiren Rijiju','Priyanka Chopra']
#persons = ['Vladimir Putin','Steve Jobs','Nelson Mandela','Albert Einstein','Emma Watson']
#nationality = {'Vladimir Putin':'RU-SP',',Steve Jobs':'US-CA','Nelson Mandela':'SA-CP','Albert Einstein':'DE-BW','Emma Watson':'UK-LDN'}
#persons = ['Cristiano Ronaldo','William Shakespeare','Leonardo da Vinci','Michael Jackson','Beyoncé']
#nationality = {'Cristiano Ronaldo':'PT','William Shakespeare':'UK-LDN','Leonardo da Vinci':'IT','Michael Jackson':'US-IN','Beyoncé':'US-TX'}
#persons = ['Dwayne Johnson','Justin Bieber','Lionel Messi','Rihanna','Selena Gomez']
#nationality = {'Dwayne Johnson':'US-CA','Justin Bieber':'CAN-ON','Lionel Messi':'ARG-SF','Rihanna':'BB-SM','Selena Gomez':'US-TX'}
# persons = ['Anushka Shetty','Kamal Haasan','Mary Kom','Akshay Kumar','Amitabh Bachchan']
#nationality = {'Anushka Shetty':'IN-KA','Kamal Haasan':'IN-TN','Mary Kom':'IN-MN','Akshay Kumar':'IN-PB','Amitabh Bachchan':'IN-UP'}
