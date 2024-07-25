THIS README WAS LAST UPDATED IN FULL ON 23/7/24. HISTORY OF SUBSTANTIAL UPDATES IS AT THE FOOT OF THIS DOCUMENT.

===

# OVERVIEW

Flawcastr is an open-source project with an AGPL v3 license (no CLAs).

Flawcastr is an application that allows users to "flawcast" their financial future, based on a variety of assumptions that the user can adjust dynamically. The term "flawcast" is used deliberately. Any scenario created with this tool WILL BE WRONG. Flawcastr might be a useful tool for gaining perspective and informing decision-making, but a user should never get the impression that it resembles a crystal ball.

Flawcastr is, in essence, a single-page application with three columns. The central, middle column shows a line chart, which allows users to visualise the value of their investment assets over the course of their lives, based on the assumptions they have chosen.

The left column allows allows the user to scroll down and see a number of different variables, and adjust these variables as they wish. As they make changes, the line chart dynamically updates. There are some additional functionalities that allow the  user to compare scenarios against each other, and there is also some basic Monte Carlo functionality.

By adjusting these assumptions, a user can get a sense of whether they are on-track financially. They can also get an appreciation of the long-term implications of some of the financial and lifestyle decisions available to them.

The ultimate goal for Flawcastr is to create a freely-available resource that millions of people can use in order to get a sense of their financial trajectories and the long-term implications of their financial decisions. The aspiration is for Flawcastr to be considered one of the best retirement calculators and maintain this reputation due to ongoing maintenance and improvements. The aim is for Flawcastr to be so useful and beneficial that is even used by financial advice professionals when engaging with clients. 

===

# CURRENT STATE

Context for this project (July 2024, around the time it was first made available on Github) can be found here: https://sonniebailey.com/flawcastr-open-source-project/.

Flawcastr is not quite ready for distribution (even as a beta version) but it is close.

The immediate aim is to get a minimum viable product (MVP) available for distribution for New Zealand users (Kiwis). Some areas that require attention are set out below under KNOWN ISSUES.

Additional improvements are set out below under FUTURE IMPROVEMENTS. This includes, for example, extending the capabilities of Flawcastr so it can be used by people in different parts of the world.

===

# CONTRIBUTION REQUEST/GUIDELINES

Flawcastr is in early stages of development. Assistance is required to help create guidelines and an effective framework for future contributions. 

Initially, I (Sonnie) would like to engage with contributors directly. Refer to my article here: https://sonniebailey.com/flawcastr-open-source-project/ for context. In short, I have a lot of relevant domain expertise, but my expertise in relation to software development is limited. Guidance in a variety of areas would be appreciated.

To contribute to this project, please contact Sonnie Bailey via sonnie.bailey@outlook.com.

===

# SETUP INSTRUCTIONS 

Providing setup instructions is one area I need help with! My hope and expectation is that this easy, given that it is a project that consists of a limited number of Python modules. 

For running via the .py modules, run from Flawcastr.py. Make sure Python has been installed and that all relevant dependencies have also been installed. To ensure this is the case:

pip install matplotlib, PyQt, prettytable, numpy, datetime, variables, typing

===

# PROJECT OVERVIEW (TECHNICAL):

## MODULES

Flawcastr consists of various modules:

* config.py, which establishes all of the relevant variables. (In future versions, many of these variables are likely to be contained in classes rather than as variables.)

* calcs.py, which makes calculations based on the variables

* viz.py, which sets out how the variables and calculations are visualised for the user. This includes the general layout of the application, as well as the chart that visualises the client's financial trajectory

* viz_widgets.py, which focuses on what items show up in the left column established in viz.py. This also explains what happens when items change (which in turn change the variables in config and calcs and that are charted)

* flawcastr.py, which brings it all together. This is the script that runs. 

Essentially, configs.py holds the varaibles. Calcs makes calculations based on these variables. Viz and viz_widgets chart the outcomes of these calculations. Viz (via viz_widgets) allows the user to update variables in config, which then update calcs and what is plotted on the chart. 

## DEPENDENCIES 

Libraries that are currently being used in this project:

* matplotlib
* PyQt
* prettytable
* numpy
* datetime 
* variables
* typing

===

# ISSUES THAT REQUIRE IMMEDIATE ATTENTION (AS AT 23 JULY 2024):

* Some calculations are anchoring to the incorrect age. 

* Additional validation of calculations is required. 

These are discussed in more detail here: https://sonniebailey.com/flawcastr-open-source-project/

Once these are addressed, an initial alpha/beta version of Flawcastr should be ready to be packaged and shared with people who are interested, in order to receive initial feedback that will inform the future of the project.

===

# FUTURE IMPROVEMENTS

* Improving the appearance of Flawcastr! It’s pretty utilitarian at the moment.

* Making Flawcastr available via browser rather than a packaged Python app. (On that note, when I package Flawcastr as an .exe it approaches 200MB in size, which seems ridiculous!)

* Developing Flawcastr so it is useful for people outside of New Zealand. One of the reasons I’ve made it for a Kiwi audience is because I live in New Zealand. Another is because I’m familiar with New Zealand’s regulatory regime and I am confident that Flawcastr won’t trigger any local regulatory issues, whereas I am not sure about other jurisdictions. Another important reason is because New Zealand has a unique pension and retirement saving regime, which makes it very simple compared to other countries. Specifically, New Zealand has a universal pension regime – so long as you meet the eligibility requirements, you receive the same pension as everyone else, regardless of your asset and income position (with some, but not many, caveats). The flip side of this is that because New Zealand is so generous with pension payments, it doesn’t provide the same type of incentives for saving for retirement, such as concessional tax treatment (which is the case for 401Ks, IRAs, and the like). Once Flawcastr is shown to be useful for Kiwis, people in other countries might want to make changes to accommodate idiosyncrasies that might relate to their own country(ies).

* Improving wording throughout the app – ie, for the right column, explanations when users hover over certain variables (not to mention, how these explanations are triggered! they are currently inconsistent), and improved documentation.

* For some variables, allow for even more nuance. At the moment, for instance, there are three variables relating directly to savings rate: current savings rate, age savings rate changes, and updated savings rate after this change. (Retirement age is also relevant, since savings stops at that point.) Ideally, the user would be able to adjust savings rate manually – ie choose savings rates assumptions for each year of their working life, and/or choose additional methodologies for how they will save (eg increase inflation-adjusted savings rate by 2% from ages 30 to 50).

* Allowing users to save scenarios (and perhaps even different user profiles).

* Allow users to export scenarios to other file formats such as CSV.

* Improve the general coding. When I started this project, I was a total noob when it comes to software development. I am conscious that there are many, many parts of the code base that are sub-optimal, and one of my sticking points with making this publicly available is that I'm embarrassed about this! For example, this project uses a lot of individual variables that should probably be treated as classes. In fact, early iterations of the project included classes instead of variables. The decision to use variables (even against the recommendations of ChatGPT/Claude!) was simply because there were too many other moving parts that I was focusing on, and using variables was more intuitive and less abstract to me than using classes at the time. Flawcastr as it currently stands wouldn't exist if I had not made that choice. At the moment I haven't explicitly followed any coding standards, commenting is spotty, and Claude and ChatGPT are always telling me I need more testing in my code.

* Allow for different options relating to less-deterministic analyses:
        
    * Allow for different methodologies for generating Monte Carlo analyses – at the moment, the way investment returns are ~randomly generated is very basic. There are lots of different ways one could do this, and it would be great to let users have the option to try different approaches.
	
	* Instead of Monte Carlo analysis for investment returns, use historical returns for historical back-testing, akin to how [FIRECalc](https://firecalc.com/) operates. 
	
	* Allow for ~randomness for variables other than investment returns (for example, savings rates and retirement expenditure)

* Overlay conditional life expectancy statistics so people can contextualise their financial position against the likelihood that they might be alive (and even allowing for more nuance than this – for instance, charting 90th percentile life expectancy instead of median expectancy; adding factors such as smoking status, personal and family health, to inform these charts; etc).

* Accommodate leverage/borrowing-to-invest. In New Zealand, for instance, there are lots of people who want to think about borrowing money to invest in property. This has its own complexities – among other things, it can magnify returns and losses. As it currently stands, Flawcastr doesn't accommodate for this. To the extent Flawcastr might be useful for someone considering whether to borrow to invest, it is most likely in terms of identifying whether it's necessary to borrow to invest – ie, to take on additional risk to achieve potentially better outcomes. 

* MAYBE make allowance for inflation. I am quite conflicted about this. As it stands, Flawcastr deals with inflation in a very specific way. Everything that is shown in the assumptions, or everything in the chart it generates, should be thought of in terms of today's dollars. If you're looking at a balance of $500,000 in 20 years' time, or you're referring to a one-off incoming or outgoing of $500,000 in 20 years' time, it is meant to represent what $500,000 can buy today, even though the exact dollar figure will probably be higher. The only concession necessary to make this to work is to **make sure that assumptions about investment returns are adjusted for inflation**. Ie, if the user thinks they might generate a return of 7%, and that inflation will be around 3%, then the figure you should put is 4%. Similarly, if the user is making assumptions about how much something will cost in the future, they need to think of it in today's dollars – for example, if they plan to downsize/rightsize your home in 50 years' time, you need to think about how much capital you might free up in today's dollars, not in terms of what the house might be worth at the time. This isn't ideal or perfect, because it assumes that inflation will impact everything at the same, constant rate. For instance, that retirement expenditure will increase at exactly the same rate as pension income. In reality, inflation impacts different people, and different parts of our financial lives, differently, over different periods of time. Personally, I believe this is a good balance of simplicity along with providing a flawed-but-useful-or-insightful perspective. Even if inflation was factored in, ideally there would be different inflation rates for different items, which makes things even more complicated and less intuitive for a user who can simply look at a chart and look at what it represents in terms of today's buying power. 

* Automating scenarios, either ~mechanistically or integrating with an LLM API. For example, automating scenarios that involve extended time out of the workforce due to illness, and contrasting this with the cost of premiums for income protection insurance. 

===

# REGULATORY CONCERNS 

## NEW ZEALAND

My intepretation of the Financial Markets Conduct Act (New Zealand) is that nothing generated by this tool represents a financial planning service. It doesn't go anywhere towards recommending any particular type of financial product (or financial product generally). Nor does this go anywhere towards developing a financial plan. It might inform how someone's financial plan but it can't be seen as a plan on its own, and makes no suggestions whatsoever regarding what someone should do. 

It is also worth noting that Flawcastr is being offered as an open-source project. Contributors are not working on this project for personal interest but to provide a useful tool for others. (This is relevant because many regulatory requirements are triggered when offered "in the business of providing" certain types of services.)

## OTHER JURISDICTIONS

If and when Flawcastr is updated to operate in other countries, regulatory concerns should be considered on a case-by-case basis. 

===

# README UPDATES

* Document first created 23/7/24