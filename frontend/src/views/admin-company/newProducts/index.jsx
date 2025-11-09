import ComplexForm from "./components/MyComplexForm";

const Dashboard = () => {
  return (
    <div className="flex w-full flex-col gap-5">
      <div className="mt-3 grid grid-cols-1 gap-5 lg:grid-cols-12">
        <div className="col-span-12 lg:!mb-0">
          <ComplexForm />
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
