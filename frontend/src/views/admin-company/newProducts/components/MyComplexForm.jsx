import React, { useState } from "react";
import Card from "components/card";
import { useAppSelector } from "store/hooks";
import { company_id as DEFAULT_COMPANY_ID } from "constants";
import { API_ENDPOINTS } from "config/api";

export default function ProductCreateCard() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [imageUrl, setImageUrl] = useState("");
  const [tags, setTags] = useState(""); // comma separated
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState("");
  const [submitSuccess, setSubmitSuccess] = useState(false);
  
  const { company_id } = useAppSelector((state) => state.company);
  const activeCompanyId = company_id || DEFAULT_COMPANY_ID;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);
    setSubmitError("");
    setSubmitSuccess(false);

    try {
      const token = localStorage.getItem('authToken');
      
      // Prepare product data matching the API format exactly
      const productData = {
        company_id: activeCompanyId,
        name: name.trim(),
        description: description.trim() || undefined,
        price: price ? parseFloat(price) : undefined,
        tags: tags.trim() ? tags.split(",").map(t => t.trim()).filter(Boolean).join(", ") : undefined,
        img_url: imageUrl.trim() || undefined,
      };

      // Remove undefined fields to match API expectations
      Object.keys(productData).forEach(key => {
        if (productData[key] === undefined) {
          delete productData[key];
        }
      });

      const response = await fetch(API_ENDPOINTS.PRODUCTS, {
        method: "POST",
        headers: {
          "accept": "application/json",
          "Content-Type": "application/json",
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify(productData),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: response.statusText }));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      console.log("Product created successfully:", result);

      setSubmitSuccess(true);
      // Reset form
      setName("");
      setDescription("");
      setPrice("");
      setImageUrl("");
      setTags("");
      
      // Clear success message after 3 seconds
      setTimeout(() => setSubmitSuccess(false), 3000);
    } catch (error) {
      console.error("Error creating product:", error);
      setSubmitError(error.message || "Failed to create product. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card extra={"w-full p-6"}>
      {/* Header */}
      <div className="mb-6">
        <h2 className="text-2xl font-bold text-navy-700 dark:text-white">
          Create New Product
        </h2>
        <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
          Fill in the details below to add a new product to your catalog
        </p>
      </div>

      <form onSubmit={handleSubmit} className="flex flex-col gap-5">
        {/* Product Name Field */}
        <div className="flex flex-col gap-2">
          <label className="text-sm font-bold text-navy-700 dark:text-white">
            Product Name <span className="text-red-500">*</span>
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter product name"
            className="w-full rounded-lg border border-gray-300 bg-white p-3 text-sm dark:border-gray-600 dark:bg-navy-700 dark:text-white"
            required
          />
        </div>

        {/* Description Field */}
        <div className="flex flex-col gap-2">
          <label className="text-sm font-bold text-navy-700 dark:text-white">
            Description
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Enter product description"
            rows={4}
            className="w-full rounded-lg border border-gray-300 bg-white p-3 text-sm dark:border-gray-600 dark:bg-navy-700 dark:text-white"
          />
        </div>

        {/* Price and Image URL Row */}
        <div className="grid grid-cols-1 gap-5 md:grid-cols-2">
          {/* Price Field */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold text-navy-700 dark:text-white">
              Price <span className="text-red-500">*</span>
            </label>
            <div className="relative">
              <span className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500">$</span>
              <input
                type="number"
                step="0.01"
                min="0"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                placeholder="0.00"
                className="w-full rounded-lg border border-gray-300 bg-white p-3 pl-8 text-sm dark:border-gray-600 dark:bg-navy-700 dark:text-white"
                required
              />
            </div>
          </div>

          {/* Image URL Field */}
          <div className="flex flex-col gap-2">
            <label className="text-sm font-bold text-navy-700 dark:text-white">
              Image URL
            </label>
            <input
              type="url"
              value={imageUrl}
              onChange={(e) => setImageUrl(e.target.value)}
              placeholder="https://example.com/image.jpg"
              className="w-full rounded-lg border border-gray-300 bg-white p-3 text-sm dark:border-gray-600 dark:bg-navy-700 dark:text-white"
            />
            {imageUrl && (
              <div className="mt-2">
                <p className="mb-2 text-xs text-gray-500 dark:text-gray-400">
                  Image Preview:
                </p>
                <div className="relative h-32 w-full overflow-hidden rounded-lg border border-gray-300 dark:border-gray-600">
                  <img
                    src={imageUrl}
                    alt="Product preview"
                    className="h-full w-full object-cover"
                    onError={(e) => {
                      e.target.style.display = "none";
                      e.target.nextSibling.style.display = "flex";
                    }}
                  />
                  <div className="hidden h-full w-full items-center justify-center bg-gray-100 text-xs text-gray-500 dark:bg-navy-700 dark:text-gray-400">
                    Invalid image URL
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Tags Field */}
        <div className="flex flex-col gap-2">
          <label className="text-sm font-bold text-navy-700 dark:text-white">
            Tags
          </label>
          <input
            type="text"
            value={tags}
            onChange={(e) => setTags(e.target.value)}
            placeholder="Enter tags (comma separated)"
            className="w-full rounded-lg border border-gray-300 bg-white p-3 text-sm dark:border-gray-600 dark:bg-navy-700 dark:text-white"
          />
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Separate multiple tags with commas (e.g., electronics, gadgets, tech)
          </p>
        </div>


        {/* Error Message */}
        {submitError && (
          <div className="rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
            {submitError}
          </div>
        )}

        {/* Success Message */}
        {submitSuccess && (
          <div className="rounded-lg bg-green-50 p-3 text-sm text-green-600 dark:bg-green-900/20 dark:text-green-400">
            Product created successfully!
          </div>
        )}

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className="linear mt-2 flex items-center justify-center rounded-xl bg-brand-500 px-6 py-3 text-base font-medium text-white transition duration-200 hover:bg-brand-600 active:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50 dark:bg-brand-400 dark:text-white dark:hover:bg-brand-300 dark:active:bg-brand-200"
        >
          {isSubmitting ? "Creating..." : "Create Product"}
        </button>
      </form>
    </Card>
  );
}