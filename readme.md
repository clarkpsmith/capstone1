**Description**

*At Home Chef* is a recipe/cooking website that allows users to look up recipes, add reviews/comments, save recipes to their user profile, and easily send ingredient lists to their email with the click of a button. It uses recipe data from the Spoonacular Recipe API. Recipe List Sending is done using the Sendgrid API. 

Recipe's can be searched by name with an optional filter for dietary restrictions or search by ingredients. There is also a seasonal dishes page that serves the user dish ideas based on the season or holiday that updates everytime the page is loaded. These feature can be used without the need for a user profile. 

Creating a user profile gives the user the ability to save favorite recipes and access a list of favorited recipes from their user page. (the user's favorite recipe list is ordered by favorited date with most recently favorited at the top)

Creating a user profile also allows the user to comment/review recipes that are visible to anyone using the site along with the ability to send an ingredient list to their email at the click of a button. 

User passwords are hashed using Bcrypt encryption and stored as encrypted data.

You can visit the site at [https://at-home-chef.herokuapp.com/
]()

**Front End Tech Stack**

(HTML, CSS, Javascript)
	 
**Back End Tech Stack**

(Python, Flask, PostgreSQL, SQlalchemy, WTF Forms)

**API's**

[https://spoonacular.com/food-api/ ]()

[https://sendgrid.com/]()
 