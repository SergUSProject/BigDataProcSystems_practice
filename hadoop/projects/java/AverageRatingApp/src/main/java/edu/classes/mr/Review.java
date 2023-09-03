package edu.classes.mr;

import com.google.gson.annotations.SerializedName;

public class Review {

    @SerializedName("asin")
    private String productId;

    @SerializedName("overall")
    private Float rating;

    public Review(String productId, Float rating) {
        this.productId = productId;
        this.rating = rating;
    }

    public String getProductId() {
        return productId;
    }

    public Float getRating() {
        return rating;
    }
}
