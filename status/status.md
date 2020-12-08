# Status Report

#### Your name

Darius Jing
Trenton Johnson

#### Your section leader's name

Reese Wynn
Spencer Strelsov

#### Project title

Finance 2.0

***

Short answers for the below questions suffice. If you want to alter your plan for your project (and obtain approval for the same), be sure to email your section leader directly!

#### What have you done for your project so far?

Input trades, calculates cost basis and cash amount for you
Automatically tracks allocation by sector and user-defined style
Chart and company overview by stock
News by stock

#### What have you not done for your project yet?

More specific metrics (eg margins, rev growth). Way to select which metrics you want to look at
Find a way to track portfolio value over time (might be tough ... would probably involve running this on a server and calling a function every day)
A how to use page
Sort index positions by ______
Market overview page. would show gen news about economy, widgets to show S&P500 performance, etc

#### What problems, if any, have you encountered?

Super slow to call the API every time you load your positions, especially once you get 10+ positions
Fix: Added a prices table that calculates prices 3 times a day with an option to manually update the prices. Makes it faster and saves API calls
Ideally, the more people that use this and update their prices, the faster it'd be for everyone

