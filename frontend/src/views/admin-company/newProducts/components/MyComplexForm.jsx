import React, { useState } from "react";

export default function ProductCreateCard() {
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [tags, setTags] = useState(""); // comma separated
  const [files, setFiles] = useState([]);

  const handleSubmit = async (e) => {
    e.preventDefault();

    const formData = new FormData();
    formData.append("name", name);
    formData.append("description", description);
    formData.append("price", price);

    tags.split(",").map(t => t.trim()).filter(Boolean).forEach(t => {
      formData.append("tags", t);
    });

    files.forEach(f => formData.append("files", f));

    await fetch("/api/products", {
      method: "POST",
      body: formData
    });
  };

  return (
    <div className="max-w-lg mx-auto bg-white rounded-2xl p-12 mt-10">
      <h2 className="text-2xl font-bold mb-4 text-slate-900">Create Product</h2>
      <form onSubmit={handleSubmit} className="flex flex-col gap-4">
        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700">Product Name</label>
          <input className="border border-slate-300 bg-slate-50 rounded-lg p-2" value={name} onChange={e => setName(e.target.value)} required />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700">Description</label>
          <textarea className="border border-slate-300 bg-slate-50 rounded-lg p-2" value={description} onChange={e => setDescription(e.target.value)} />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700">Price</label>
          <input type="number" className="border border-slate-300 bg-slate-50 rounded-lg p-2" value={price} onChange={e => setPrice(e.target.value)} />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700">Tags (comma separated)</label>
          <input className="border border-slate-300 bg-slate-50 rounded-lg p-2" value={tags} onChange={e => setTags(e.target.value)} />
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-sm font-medium text-slate-700">Ad Files</label>
          <input type="file" multiple onChange={e => setFiles(Array.from(e.target.files))} className="border border-slate-300 bg-slate-50 rounded-lg p-2" />
        </div>
<button
          href=" "
          className="linear mt-4 flex items-center justify-center rounded-xl bg-brand-500 px-2 py-2 text-base font-medium text-white transition duration-200 hover:bg-brand-600 active:bg-brand-700 dark:bg-brand-400 dark:text-white dark:hover:bg-brand-300 dark:active:bg-brand-200"
        >
          Create Product
        </button>
      </form>
    </div>
  );
}