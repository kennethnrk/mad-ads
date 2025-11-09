import ComplexForm from "./components/MyComplexForm";

const Dashboard = () => {
  return (
    <div>
      {/* Card widget */}

    {/* first column width is 3/4 and second column width is 1/4 */}
      <div className="mt-5 grid grid-cols-1 gap-5 xl:grid-cols-1">
         {/* Complex Table width is 3/4 */}

        <div className="grid grid-cols-1 gap-5 rounded-[20px] bg-white p-4 shadow-lg ">
          <ComplexForm onSubmit={(data) => {
            // Handle form submission
            console.log("Form submitted", data);
          }} />
        </div>

      </div>
    </div>
  );
};

export default Dashboard;
