import React from "react";
import CardMenu from "components/card/CardMenu";
import Card from "components/card";
import Progress from "components/progress";
import { MdCancel, MdCheckCircle, MdOutlineError, MdClose } from "react-icons/md";
import { getProducts, uploadAd } from "services/api";
import { useAppSelector } from "store/hooks";
import { company_id as DEFAULT_COMPANY_ID } from "constants";

import {
  createColumnHelper,
  flexRender,
  getCoreRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table";

const columnHelper = createColumnHelper();

// const columns = columnsDataCheck;
export default function ComplexTable(props) {
  const { tableData } = props;
  const [sorting, setSorting] = React.useState([]);
  let defaultData = tableData;
  const [data, setData] = React.useState(() => [...defaultData]);
  const [loading, setLoading] = React.useState(false);
  const [error, setError] = React.useState(null);
  const { company_id } = useAppSelector((state) => state.company);
  const [isModalOpen, setIsModalOpen] = React.useState(false);
  const [selectedProduct, setSelectedProduct] = React.useState(null);
  const [uploadFile, setUploadFile] = React.useState(null);
  const [uploading, setUploading] = React.useState(false);
  const [uploadError, setUploadError] = React.useState(null);
  const [uploadSuccess, setUploadSuccess] = React.useState(false);
  const [adTitle, setAdTitle] = React.useState("");
  const [adDescription, setAdDescription] = React.useState("");
  const [adTags, setAdTags] = React.useState("");

  const handleOpenModal = (product) => {
    setSelectedProduct(product);
    setIsModalOpen(true);
    setUploadFile(null);
    setUploadError(null);
    setUploadSuccess(false);
    setAdTitle("");
    setAdDescription("");
    setAdTags("");
  };

  const columns = [
    columnHelper.accessor("name", {
      id: "name",
      header: () => (
        <p className="text-sm font-bold text-gray-600 dark:text-white">NAME</p>
      ),
      cell: (info) => (
        <p className="text-sm font-bold text-navy-700 dark:text-white">
          {info.getValue()}
        </p>
      ),
    }),
    columnHelper.accessor("description", {
      id: "description",
      header: () => (
        <p className="text-sm font-bold text-gray-600 dark:text-white">
          DESCRIPTION
        </p>
      ),
      cell: (info) => (
        <div className="flex items-center">
          {info.getValue().length > 50 ? (
            <p className="text-sm font-bold text-navy-700 dark:text-white">
              {info.getValue().substring(0, 50)}...
            </p>
          ) : (
            <p className="text-sm font-bold text-navy-700 dark:text-white">
              {info.getValue()}
            </p>
          )}
        </div>
      ),
    }),
    columnHelper.accessor("price", {
      id: "price",
      header: () => (
        <p className="text-sm font-bold text-gray-600 dark:text-white">PRICE</p>
      ),
      cell: (info) => (
        <p className="text-sm font-bold text-navy-700 dark:text-white">
          {info.getValue()}
        </p>
      ),
    }),
    columnHelper.accessor("tags", {
      id: "tags",
      header: () => (
        <p className="text-sm font-bold text-gray-600 dark:text-white">
          TAGS
        </p>
      ),
      cell: (info) => (
        <div className="flex items-center">
          {info.getValue().length > 30 ? (
            <p className="text-sm font-bold text-navy-700 dark:text-white">
              {info.getValue().substring(0, 30)}... 
            </p>
          ) : (
            <p className="text-sm font-bold text-navy-700 dark:text-white">
              {info.getValue()}
            </p>
          )}
        </div>
      ),
    }),
    columnHelper.display({
      id: "actions",
      header: () => (
        <p className="text-sm font-bold text-gray-600 dark:text-white">
          ACTIONS
        </p>
      ),
      cell: (info) => (
        <button 
          onClick={() => handleOpenModal(info.row.original)}
          className="flex h-8 w-8 items-center justify-center rounded-full bg-blue-500 text-white hover:bg-blue-600 transition-colors"
        >
          <span className="text-lg font-bold">+</span>
        </button>
      ),
    }),
  ]; // eslint-disable-next-line

  // Fetch products from API on component mount and when company_id changes
  React.useEffect(() => {
    const fetchProducts = async () => {
      setLoading(true);
      setError(null);
      try {
        const params = { skip: 0, limit: 100 };
        // Use Redux company_id if set, otherwise use default from constants
        const activeCompanyId = company_id || DEFAULT_COMPANY_ID;
        if (activeCompanyId) {
          params.company_id = activeCompanyId;
        }
        const products = await getProducts(params);
        if (products && Array.isArray(products)) {
          setData(products);
        }
      } catch (err) {
        console.error('Failed to fetch products:', err);
        setError(err.message || 'Failed to fetch products');
        // Keep default data on error
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, [company_id]);

  const handleCloseModal = () => {
    setIsModalOpen(false);
    setSelectedProduct(null);
    setUploadFile(null);
    setUploadError(null);
    setUploadSuccess(false);
    setAdTitle("");
    setAdDescription("");
    setAdTags("");
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setUploadFile(file);
      setUploadError(null);
      setUploadSuccess(false);
    }
  };

  const handleUpload = async () => {
    if (!uploadFile) {
      setUploadError("Please select a file to upload");
      return;
    }

    if (!adTitle.trim()) {
      setUploadError("Please enter a title");
      return;
    }

    if (!adDescription.trim()) {
      setUploadError("Please enter a description");
      return;
    }

    if (!selectedProduct?.id) {
      setUploadError("Please select a product");
      return;
    }

    setUploading(true);
    setUploadError(null);
    setUploadSuccess(false);

    try {
      // Use company_id from store, fallback to default
      const ownerId = company_id || DEFAULT_COMPANY_ID;
      
      const result = await uploadAd({
        file: uploadFile,
        owner_id: ownerId,
        product_id: selectedProduct.id,
        title: adTitle,
        description: adDescription,
        tags: adTags || undefined,
      });

      console.log("Ad uploaded successfully:", result);
      setUploadSuccess(true);
      setTimeout(() => {
        handleCloseModal();
      }, 1500);
    } catch (err) {
      console.error("Upload error:", err);
      setUploadError(err.message || "Failed to upload ad");
    } finally {
      setUploading(false);
    }
  };

  const table = useReactTable({
    data,
    columns,
    state: {
      sorting,
    },
    onSortingChange: setSorting,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    debugTable: true,
  });
  return (
    <Card extra={"w-full h-full px-6 pb-6 sm:overflow-x-auto"}>
      <div className="relative flex items-center justify-between pt-4">
        <div className="text-xl font-bold text-navy-700 dark:text-white">
          Complex Table
        </div>
        <CardMenu />
      </div>

      {loading && (
        <div className="mt-8 flex items-center justify-center py-8">
          <p className="text-sm text-gray-600 dark:text-white">Loading products...</p>
        </div>
      )}
      {error && (
        <div className="mt-8 flex items-center justify-center py-8">
          <p className="text-sm text-red-600 dark:text-red-400">Error: {error}</p>
        </div>
      )}
      {!loading && !error && (
        <div className="mt-8 max-h-[200px] overflow-auto">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="sticky top-0 z-10 bg-white dark:bg-navy-800">
                {table.getHeaderGroups().map((headerGroup) => (
                  <tr key={headerGroup.id} className="!border-px !border-gray-400">
                    {headerGroup.headers.map((header) => {
                      return (
                        <th
                          key={header.id}
                          colSpan={header.colSpan}
                          onClick={header.column.getToggleSortingHandler()}
                          className="cursor-pointer border-b-[1px] border-gray-200 pt-4 pb-2 pr-4 text-start"
                        >
                          <div className="items-center justify-between text-xs text-gray-200">
                            {flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                            {{
                              asc: "",
                              desc: "",
                            }[header.column.getIsSorted()] ?? null}
                          </div>
                        </th>
                      );
                    })}
                  </tr>
                ))}
              </thead>
              <tbody>
                {table
                  .getRowModel()
                  .rows.map((row) => {
                    return (
                      <tr key={row.id}>
                        {row.getVisibleCells().map((cell) => {
                          return (
                            <td
                              key={cell.id}
                              className="min-w-[150px] border-white/0 py-3  pr-4"
                            >
                              {flexRender(
                                cell.column.columnDef.cell,
                                cell.getContext()
                              )}
                            </td>
                          );
                        })}
                      </tr>
                    );
                  })}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* Upload Ad Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black bg-opacity-50">
          <div className="relative w-full max-w-md max-h-[90vh] overflow-y-auto rounded-xl bg-white p-6 shadow-xl dark:bg-navy-800">
            {/* Close Button */}
            <button
              onClick={handleCloseModal}
              className="absolute right-4 top-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
            >
              <MdClose className="h-6 w-6" />
            </button>

            {/* Modal Header */}
            <div className="mb-4">
              <h2 className="text-2xl font-bold text-navy-700 dark:text-white">
                Upload Ad
              </h2>
              {selectedProduct && (
                <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                  For: {selectedProduct.name}
                </p>
              )}
            </div>

            {/* Title Field */}
            <div className="mb-4">
              <label className="mb-2 block text-sm font-bold text-navy-700 dark:text-white">
                Title <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                value={adTitle}
                onChange={(e) => setAdTitle(e.target.value)}
                placeholder="Enter ad title"
                className="w-full rounded-lg border border-gray-300 bg-white p-2 text-sm dark:border-gray-600 dark:bg-navy-700 dark:text-white"
                required
              />
            </div>

            {/* Description Field */}
            <div className="mb-4">
              <label className="mb-2 block text-sm font-bold text-navy-700 dark:text-white">
                Description <span className="text-red-500">*</span>
              </label>
              <textarea
                value={adDescription}
                onChange={(e) => setAdDescription(e.target.value)}
                placeholder="Enter ad description"
                rows={4}
                className="w-full rounded-lg border border-gray-300 bg-white p-2 text-sm dark:border-gray-600 dark:bg-navy-700 dark:text-white"
                required
              />
            </div>

            {/* Tags Field */}
            <div className="mb-4">
              <label className="mb-2 block text-sm font-bold text-navy-700 dark:text-white">
                Tags
              </label>
              <input
                type="text"
                value={adTags}
                onChange={(e) => setAdTags(e.target.value)}
                placeholder="Enter tags (comma separated)"
                className="w-full rounded-lg border border-gray-300 bg-white p-2 text-sm dark:border-gray-600 dark:bg-navy-700 dark:text-white"
              />
              <p className="mt-1 text-xs text-gray-500 dark:text-gray-400">
                Separate multiple tags with commas
              </p>
            </div>

            {/* File Upload */}
            <div className="mb-4">
              <label className="mb-2 block text-sm font-bold text-navy-700 dark:text-white">
                Select Ad File <span className="text-red-500">*</span>
              </label>
              <input
                type="file"
                onChange={handleFileChange}
                accept="video/*"
                className="w-full rounded-lg border border-gray-300 bg-white p-2 text-sm dark:border-gray-600 dark:bg-navy-700 dark:text-white"
              />
              {uploadFile && (
                <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
                  Selected: {uploadFile.name}
                </p>
              )}
            </div>

            {/* Error Message */}
            {uploadError && (
              <div className="mb-4 rounded-lg bg-red-50 p-3 text-sm text-red-600 dark:bg-red-900/20 dark:text-red-400">
                {uploadError}
              </div>
            )}

            {/* Success Message */}
            {uploadSuccess && (
              <div className="mb-4 rounded-lg bg-green-50 p-3 text-sm text-green-600 dark:bg-green-900/20 dark:text-green-400">
                Ad uploaded successfully!
              </div>
            )}

            {/* Action Buttons */}
            <div className="flex gap-3">
              <button
                onClick={handleCloseModal}
                disabled={uploading}
                className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-50 dark:border-gray-600 dark:bg-navy-700 dark:text-white dark:hover:bg-navy-600"
              >
                Cancel
              </button>
              <button
                onClick={handleUpload}
                disabled={uploading || !uploadFile || !adTitle.trim() || !adDescription.trim()}
                className="flex-1 rounded-lg bg-blue-500 px-4 py-2 text-sm font-medium text-white hover:bg-blue-600 disabled:cursor-not-allowed disabled:opacity-50"
              >
                {uploading ? "Uploading..." : "Upload"}
              </button>
            </div>
          </div>
        </div>
      )}
    </Card>
  );
}
