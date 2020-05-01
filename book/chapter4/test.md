# Manually Testing Your Step Function

Go to your Step Function in the console.

<img src="./Screen-Shot-2020-04-16-at-11.34.12-PM-1024x562.png"></img>

Click the Start Execution button; again, just use the default JSON in there. Sit there and wait for her to finish. At the time of this writing, the page does auto-refresh and you can see the execution event history list below update dynamically. Once it gets to 100, you have to manually load more, but you don't have to. However, I've seen longer functions sometimes not refresh the page. Your function may be done, but the page doesn't refresh to show it. If you get impatient like I do, just Control + R a bunch of times until she's all green, a step is red or gray.

She'll probably turn red. Click the red bubble itself, and click on "Exceptions" to the right to see why.

<img src="./Screen Shot 2020-04-25 at 10.22.05 AM.png"></img>

Cool, so our first eror in a Step Function. Now what?