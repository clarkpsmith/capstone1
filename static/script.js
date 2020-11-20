$(".favorite").on("click", ".favorited-btn", removeFavorite);
$(".favorite").on("click", ".not-favorited-btn", addFavorite);
$(".favorites").on("click", ".favorited-btn", deleteFavorite);
async function addFavorite() {
  let dishId = $(this).data("id");
  res = await axios.post(`/favorite/${dishId}`);

  $(this).removeClass("not-favorited-btn");
  $(this).html('<i class="fas fa-star"></i> Remove Dish from Favorites');
  $(this).addClass("favorited-btn");
}

async function removeFavorite() {
  let dishId = $(this).data("id");
  res = await axios.post(`/removefavorite/${dishId}`);

  $(this).removeClass("favorited-btn");
  $(this).html('<i class="fas fa-star"></i> Add Dish to Favorites');
  $(this).addClass("not-favorited-btn");
}

async function deleteFavorite() {
  let dishId = $(this).data("id");

  res = await axios.post(`/removefavorite/${dishId}`);

  $(this).closest(".liked-recipe").remove();
}
