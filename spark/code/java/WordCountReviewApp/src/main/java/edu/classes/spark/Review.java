package edu.classes.spark;

import com.google.gson.annotations.SerializedName;

public class Review {

    @SerializedName("asin")
    private String productId;

    @SerializedName("overall")
    private Float rating;

    @SerializedName("reviewText")
    private String review;

    public Review() {
    }

    public Review(String productId, Float rating, String review) {
        this.productId = productId;
        this.rating = rating;
        this.review = review;
    }

    public String getProductId() {
        return productId;
    }

    public Float getRating() {
        return rating;
    }

    public String getReview() {
        return review;
    }
}
