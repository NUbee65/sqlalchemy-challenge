# WIP!!!!

# 1. Import Flask
from flask import Flask

#%%
# 2. Create an app
app = Flask(__name__)

#%%
# 3. Define static routes
@app.route("/")
def index():
    return "Hello, world!  And a big world it is."

#%%
@app.route("/investment_thesis")
def investment_thesis():
    return "Even with burgeoning piles of data inside the enterprise and outside, artificial intelligence has thus far really only been deployed in piecemeal fashion.  Predictive analytics in supply chain management and enterprise resource planning.  Marketing analytics to demand forecasting.  AI in investment management.  Some analytics for human resource management.  And everyone talking about full integration with existing systems.  And there is limited use of AI in automating certain lower level decisions (e.g., replenishment).  And most vendors and consulting service providers in the business of developing predictive analytics systems recognize that it is very difficult to predict systematic shifts that blindside and badly damage enterprises.  What I believe is that end-to-end-and-beyond is the future.  Often visibility is limited by or altogether unavailable from proprietary data not being shared with partners.  And data content owners (e.g., demographics, financial, industry sector) charge a pretty penny for curated data.  I believe that advanced use of AI may offer a sort-of x-ray visibility around commercial networks and possibly even industrial networks.  I also believe a fully integrated end-to-end AI may offer means to gain tactical and strategic competitive advantage delivering quality products and/or services with competitive flexibility and profitability."

#%%
@app.route("/about")
def about():
    print("Server received request for 'About' page...")
    return "My name is Brooke.  I am an investment banker.  I am based in the Washington metro area"

#%%
@app.route("/contact")
def contact():
    print("Server received request for 'Contact' page...")
    return "I can be reached at 202-833-5507 x 102 or at brooke.cooper@techacumengroup.com.  Or find me on LinkedIn (https://www.linkedin.com/in/brooke-cooper-49a68183/)."

#%%
# 4. Define main behavior
if __name__ == "__main__":
    app.run(debug=True)
