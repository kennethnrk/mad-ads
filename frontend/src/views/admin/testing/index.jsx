import React, { useState } from "react";
import Card from "components/card";
import { matchContent, checkHealth, generateVariants, textToSpeech, optimizeCampaign, testSnowflakeQuery, testSnowflakeVectorSearch } from "services/api";

const TestingDashboard = () => {
  const [healthStatus, setHealthStatus] = useState(null);
  const [matchResult, setMatchResult] = useState(null);
  const [loading, setLoading] = useState({});
  const [errors, setErrors] = useState({});
  const [snowflakeQueryResult, setSnowflakeQueryResult] = useState(null);
  const [snowflakeVectorResult, setSnowflakeVectorResult] = useState(null);

  // Health Check
  const handleHealthCheck = async () => {
    setLoading({ ...loading, health: true });
    setErrors({ ...errors, health: null });
    try {
      const result = await checkHealth();
      setHealthStatus(result);
    } catch (error) {
      setErrors({ ...errors, health: error.message });
    } finally {
      setLoading({ ...loading, health: false });
    }
  };

  // Match Content
  const [matchData, setMatchData] = useState({
    content_id: "content_123",
    ad_pool_id: "",
    brief: "",
    limit: 5,
  });

  const handleMatch = async () => {
    setLoading({ ...loading, match: true });
    setErrors({ ...errors, match: null });
    try {
      const result = await matchContent(matchData);
      setMatchResult(result);
    } catch (error) {
      setErrors({ ...errors, match: error.message });
    } finally {
      setLoading({ ...loading, match: false });
    }
  };

  // Generate Variants
  const [generateData, setGenerateData] = useState({
    content_id: "content_123",
    ad_id: "ad_1",
  });

  const handleGenerate = async () => {
    setLoading({ ...loading, generate: true });
    setErrors({ ...errors, generate: null });
    try {
      const result = await generateVariants(generateData);
      console.log("Generate result:", result);
      alert("Generate API called! Check console for result.");
    } catch (error) {
      setErrors({ ...errors, generate: error.message });
    } finally {
      setLoading({ ...loading, generate: false });
    }
  };

  // TTS
  const [ttsData, setTtsData] = useState({
    text: "This is a test ad script for voice generation.",
    voice: "",
  });

  const handleTTS = async () => {
    setLoading({ ...loading, tts: true });
    setErrors({ ...errors, tts: null });
    try {
      const result = await textToSpeech(ttsData);
      console.log("TTS result:", result);
      alert("TTS API called! Check console for result.");
    } catch (error) {
      setErrors({ ...errors, tts: error.message });
    } finally {
      setLoading({ ...loading, tts: false });
    }
  };

  // Optimize
  const [optimizeData, setOptimizeData] = useState({
    goal: "maximize_clicks",
    variants: ["variant_1", "variant_2"],
    channels: ["instagram", "google_ads"],
    budget: 10000,
  });

  const handleOptimize = async () => {
    setLoading({ ...loading, optimize: true });
    setErrors({ ...errors, optimize: null });
    try {
      const result = await optimizeCampaign(optimizeData);
      console.log("Optimize result:", result);
      alert("Optimize API called! Check console for result.");
    } catch (error) {
      setErrors({ ...errors, optimize: error.message });
    } finally {
      setLoading({ ...loading, optimize: false });
    }
  };

  // Snowflake Query Test
  const [snowflakeQueryData, setSnowflakeQueryData] = useState({
    query: "SELECT * FROM MVP_PRODUCTS LIMIT 5",
    params: null,
  });

  const handleSnowflakeQuery = async () => {
    setLoading({ ...loading, snowflakeQuery: true });
    setErrors({ ...errors, snowflakeQuery: null });
    setSnowflakeQueryResult(null);
    try {
      const result = await testSnowflakeQuery({
        query: snowflakeQueryData.query,
        params: snowflakeQueryData.params ? JSON.parse(snowflakeQueryData.params) : null,
      });
      setSnowflakeQueryResult(result);
    } catch (error) {
      setErrors({ ...errors, snowflakeQuery: error.message });
    } finally {
      setLoading({ ...loading, snowflakeQuery: false });
    }
  };

  // Snowflake Vector Search Test
  const [snowflakeVectorData, setSnowflakeVectorData] = useState({
    text: "wrist hurts on bench press, need support",
    k: 5,
    columns: ["id", "name", "category", "price", "image_url"],
    filter_obj: '{"@eq": {"category": "Gear"}}',
  });

  const handleSnowflakeVectorSearch = async () => {
    setLoading({ ...loading, snowflakeVector: true });
    setErrors({ ...errors, snowflakeVector: null });
    setSnowflakeVectorResult(null);
    try {
      const filterObj = snowflakeVectorData.filter_obj ? JSON.parse(snowflakeVectorData.filter_obj) : null;
      const result = await testSnowflakeVectorSearch({
        text: snowflakeVectorData.text,
        k: snowflakeVectorData.k,
        columns: snowflakeVectorData.columns,
        filter_obj: filterObj,
      });
      setSnowflakeVectorResult(result);
    } catch (error) {
      setErrors({ ...errors, snowflakeVector: error.message });
    } finally {
      setLoading({ ...loading, snowflakeVector: false });
    }
  };

  return (
    <div className="mt-3">
      <div className="mb-5">
        <h2 className="text-2xl font-bold text-navy-700 dark:text-white">
          API Testing Dashboard
        </h2>
        <p className="mt-2 text-gray-600 dark:text-gray-400">
          Test all backend API endpoints with dummy data
        </p>
      </div>

      <div className="space-y-5">
        {/* Health Check */}
        <Card extra="!p-[20px]">
          <h3 className="text-lg font-bold text-navy-700 dark:text-white mb-4">
            Health Check
          </h3>
          <div className="space-y-4">
            <button
              onClick={handleHealthCheck}
              disabled={loading.health}
              className="linear flex items-center justify-center rounded-xl bg-brand-500 px-4 py-2 text-base font-medium text-white transition duration-200 hover:bg-brand-600 active:bg-brand-700 dark:bg-brand-400 dark:text-white dark:hover:bg-brand-300 dark:active:bg-brand-200 disabled:opacity-50"
            >
              {loading.health ? "Checking..." : "Check Backend Health"}
            </button>
            {errors.health && (
              <div className="rounded-lg bg-red-50 p-4 text-red-800 dark:bg-red-900/20 dark:text-red-200">
                <strong>Error:</strong> {errors.health}
              </div>
            )}
            {healthStatus && (
              <div className="rounded-lg bg-green-50 p-4 dark:bg-green-900/20">
                <p className="font-bold text-green-800 dark:text-green-200">
                  Status: {healthStatus.status}
                </p>
                <p className="text-green-700 dark:text-green-300">
                  Version: {healthStatus.version}
                </p>
                <p className="text-green-700 dark:text-green-300">
                  Timestamp: {new Date(healthStatus.timestamp).toLocaleString()}
                </p>
              </div>
            )}
          </div>
        </Card>

        {/* Match Content */}
        <Card extra="!p-[20px]">
          <h3 className="text-lg font-bold text-navy-700 dark:text-white mb-4">
            Match Content to Ads
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Content ID:
              </label>
              <input
                type="text"
                value={matchData.content_id}
                onChange={(e) => setMatchData({ ...matchData, content_id: e.target.value })}
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
                placeholder="content_123"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Ad Pool ID (optional):
              </label>
              <input
                type="text"
                value={matchData.ad_pool_id}
                onChange={(e) => setMatchData({ ...matchData, ad_pool_id: e.target.value })}
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
                placeholder="pool_456"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Brief (optional):
              </label>
              <textarea
                value={matchData.brief}
                onChange={(e) => setMatchData({ ...matchData, brief: e.target.value })}
                rows={3}
                className="flex w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
                placeholder="target fitness enthusiasts"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Limit:
              </label>
              <input
                type="number"
                value={matchData.limit}
                onChange={(e) => setMatchData({ ...matchData, limit: parseInt(e.target.value) || 5 })}
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
              />
            </div>
            <button
              onClick={handleMatch}
              disabled={loading.match}
              className="linear flex items-center justify-center rounded-xl bg-purple-500 px-4 py-2 text-base font-medium text-white transition duration-200 hover:bg-purple-600 active:bg-purple-700 dark:bg-purple-400 dark:text-white dark:hover:bg-purple-300 dark:active:bg-purple-200 disabled:opacity-50"
            >
              {loading.match ? "Matching..." : "Match Content"}
            </button>
            {errors.match && (
              <div className="rounded-lg bg-red-50 p-4 text-red-800 dark:bg-red-900/20 dark:text-red-200">
                <strong>Error:</strong> {errors.match}
              </div>
            )}
            {matchResult && (
              <div className="rounded-lg bg-purple-50 p-4 dark:bg-purple-900/20">
                <p className="font-bold text-purple-800 dark:text-purple-200 mb-2">
                  Match Results:
                </p>
                <div className="space-y-2">
                  {matchResult.top_k?.map((match, idx) => (
                    <div
                      key={idx}
                      className="rounded-lg bg-white p-3 border border-gray-200 dark:bg-navy-700 dark:border-navy-600"
                    >
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-bold text-navy-700 dark:text-white">
                          Ad ID: {match.ad_id}
                        </span>
                        <span className="px-2 py-1 rounded bg-green-500 text-white text-sm font-semibold">
                          Score: {match.score.toFixed(2)}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Overlap: {match.why.overlap.join(", ") || "None"}
                      </p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">
                        Cosine: {match.why.cosine.toFixed(2)} | Demo Fit:{" "}
                        {match.why.demo_fit.toFixed(2)}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        </Card>

        {/* Generate Variants */}
        <Card extra="!p-[20px]">
          <h3 className="text-lg font-bold text-navy-700 dark:text-white mb-4">
            Generate Ad Variants
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Content ID:
              </label>
              <input
                type="text"
                value={generateData.content_id}
                onChange={(e) => setGenerateData({ ...generateData, content_id: e.target.value })}
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Ad ID:
              </label>
              <input
                type="text"
                value={generateData.ad_id}
                onChange={(e) => setGenerateData({ ...generateData, ad_id: e.target.value })}
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
              />
            </div>
            <button
              onClick={handleGenerate}
              disabled={loading.generate}
              className="linear flex items-center justify-center rounded-xl bg-teal-500 px-4 py-2 text-base font-medium text-white transition duration-200 hover:bg-teal-600 active:bg-teal-700 dark:bg-teal-400 dark:text-white dark:hover:bg-teal-300 dark:active:bg-teal-200 disabled:opacity-50"
            >
              {loading.generate ? "Generating..." : "Generate Variants"}
            </button>
            {errors.generate && (
              <div className="rounded-lg bg-red-50 p-4 text-red-800 dark:bg-red-900/20 dark:text-red-200">
                <strong>Error:</strong> {errors.generate}
              </div>
            )}
          </div>
        </Card>

        {/* Text to Speech */}
        <Card extra="!p-[20px]">
          <h3 className="text-lg font-bold text-navy-700 dark:text-white mb-4">
            Text to Speech
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Text:
              </label>
              <textarea
                value={ttsData.text}
                onChange={(e) => setTtsData({ ...ttsData, text: e.target.value })}
                rows={4}
                className="flex w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
                placeholder="Enter text to convert to speech"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Voice ID (optional):
              </label>
              <input
                type="text"
                value={ttsData.voice}
                onChange={(e) => setTtsData({ ...ttsData, voice: e.target.value })}
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
                placeholder="Leave empty for default"
              />
            </div>
            <button
              onClick={handleTTS}
              disabled={loading.tts}
              className="linear flex items-center justify-center rounded-xl bg-orange-500 px-4 py-2 text-base font-medium text-white transition duration-200 hover:bg-orange-600 active:bg-orange-700 dark:bg-orange-400 dark:text-white dark:hover:bg-orange-300 dark:active:bg-orange-200 disabled:opacity-50"
            >
              {loading.tts ? "Generating Audio..." : "Generate Speech"}
            </button>
            {errors.tts && (
              <div className="rounded-lg bg-red-50 p-4 text-red-800 dark:bg-red-900/20 dark:text-red-200">
                <strong>Error:</strong> {errors.tts}
              </div>
            )}
          </div>
        </Card>

        {/* Optimize Campaign */}
        <Card extra="!p-[20px]">
          <h3 className="text-lg font-bold text-navy-700 dark:text-white mb-4">
            Optimize Campaign
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Goal:
              </label>
              <select
                value={optimizeData.goal}
                onChange={(e) => setOptimizeData({ ...optimizeData, goal: e.target.value })}
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
              >
                <option value="maximize_clicks">Maximize Clicks</option>
                <option value="maximize_conversions">Maximize Conversions</option>
                <option value="maximize_reach">Maximize Reach</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Variants (comma-separated):
              </label>
              <input
                type="text"
                value={optimizeData.variants.join(", ")}
                onChange={(e) =>
                  setOptimizeData({
                    ...optimizeData,
                    variants: e.target.value.split(",").map((v) => v.trim()).filter(Boolean),
                  })
                }
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
                placeholder="variant_1, variant_2"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Channels (comma-separated):
              </label>
              <input
                type="text"
                value={optimizeData.channels.join(", ")}
                onChange={(e) =>
                  setOptimizeData({
                    ...optimizeData,
                    channels: e.target.value.split(",").map((c) => c.trim()).filter(Boolean),
                  })
                }
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
                placeholder="instagram, google_ads"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Budget:
              </label>
              <input
                type="number"
                value={optimizeData.budget}
                onChange={(e) =>
                  setOptimizeData({ ...optimizeData, budget: parseFloat(e.target.value) || 0 })
                }
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
              />
            </div>
            <button
              onClick={handleOptimize}
              disabled={loading.optimize}
              className="linear flex items-center justify-center rounded-xl bg-green-500 px-4 py-2 text-base font-medium text-white transition duration-200 hover:bg-green-600 active:bg-green-700 dark:bg-green-400 dark:text-white dark:hover:bg-green-300 dark:active:bg-green-200 disabled:opacity-50"
            >
              {loading.optimize ? "Optimizing..." : "Optimize Campaign"}
            </button>
            {errors.optimize && (
              <div className="rounded-lg bg-red-50 p-4 text-red-800 dark:bg-red-900/20 dark:text-red-200">
                <strong>Error:</strong> {errors.optimize}
              </div>
            )}
          </div>
        </Card>

        {/* Snowflake Query Test */}
        <Card extra="!p-[20px]">
          <h3 className="text-lg font-bold text-navy-700 dark:text-white mb-4">
            Snowflake Query Test
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                SQL Query:
              </label>
              <textarea
                value={snowflakeQueryData.query}
                onChange={(e) => setSnowflakeQueryData({ ...snowflakeQueryData, query: e.target.value })}
                rows={4}
                className="flex w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white font-mono"
                placeholder="SELECT * FROM MVP_PRODUCTS LIMIT 5"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Parameters (JSON, optional):
              </label>
              <textarea
                value={snowflakeQueryData.params || ""}
                onChange={(e) => setSnowflakeQueryData({ ...snowflakeQueryData, params: e.target.value || null })}
                rows={2}
                className="flex w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white font-mono"
                placeholder='{"param1": "value1"}'
              />
            </div>
            <button
              onClick={handleSnowflakeQuery}
              disabled={loading.snowflakeQuery}
              className="linear flex items-center justify-center rounded-xl bg-blue-500 px-4 py-2 text-base font-medium text-white transition duration-200 hover:bg-blue-600 active:bg-blue-700 dark:bg-blue-400 dark:text-white dark:hover:bg-blue-300 dark:active:bg-blue-200 disabled:opacity-50"
            >
              {loading.snowflakeQuery ? "Executing Query..." : "Execute Query"}
            </button>
            {errors.snowflakeQuery && (
              <div className="rounded-lg bg-red-50 p-4 text-red-800 dark:bg-red-900/20 dark:text-red-200">
                <strong>Error:</strong> {errors.snowflakeQuery}
              </div>
            )}
            {snowflakeQueryResult && (
              <div className="rounded-lg bg-blue-50 p-4 dark:bg-blue-900/20">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-bold text-blue-800 dark:text-blue-200">
                    Query Results:
                  </p>
                  <span className={`px-2 py-1 rounded text-sm font-semibold ${
                    snowflakeQueryResult.success 
                      ? "bg-green-500 text-white" 
                      : "bg-red-500 text-white"
                  }`}>
                    {snowflakeQueryResult.success ? "Success" : "Failed"}
                  </span>
                </div>
                {snowflakeQueryResult.error && (
                  <p className="text-red-600 dark:text-red-300 mb-2">{snowflakeQueryResult.error}</p>
                )}
                {snowflakeQueryResult.results && snowflakeQueryResult.results.length > 0 && (
                  <div className="mt-2 max-h-96 overflow-y-auto">
                    <pre className="text-xs bg-white dark:bg-navy-700 p-3 rounded border border-gray-200 dark:border-navy-600 overflow-x-auto">
                      {JSON.stringify(snowflakeQueryResult.results, null, 2)}
                    </pre>
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>

        {/* Snowflake Vector Search Test */}
        <Card extra="!p-[20px]">
          <h3 className="text-lg font-bold text-navy-700 dark:text-white mb-4">
            Snowflake Cortex Vector Search
          </h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Search Text:
              </label>
              <textarea
                value={snowflakeVectorData.text}
                onChange={(e) => setSnowflakeVectorData({ ...snowflakeVectorData, text: e.target.value })}
                rows={3}
                className="flex w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
                placeholder="wrist hurts on bench press, need support"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Number of Results (k):
              </label>
              <input
                type="number"
                value={snowflakeVectorData.k}
                onChange={(e) => setSnowflakeVectorData({ ...snowflakeVectorData, k: parseInt(e.target.value) || 5 })}
                className="flex h-12 w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white"
              />
            </div>
            <div>
              <label className="block text-sm font-semibold text-navy-700 dark:text-white mb-2">
                Filter Object (JSON, optional):
              </label>
              <textarea
                value={snowflakeVectorData.filter_obj}
                onChange={(e) => setSnowflakeVectorData({ ...snowflakeVectorData, filter_obj: e.target.value })}
                rows={2}
                className="flex w-full items-center justify-center rounded-xl border border-gray-200 bg-white/0 p-3 text-sm outline-none dark:!border-navy-800 dark:bg-navy-800 dark:text-white font-mono"
                placeholder='{"@eq": {"category": "Gear"}}'
              />
            </div>
            <button
              onClick={handleSnowflakeVectorSearch}
              disabled={loading.snowflakeVector}
              className="linear flex items-center justify-center rounded-xl bg-indigo-500 px-4 py-2 text-base font-medium text-white transition duration-200 hover:bg-indigo-600 active:bg-indigo-700 dark:bg-indigo-400 dark:text-white dark:hover:bg-indigo-300 dark:active:bg-indigo-200 disabled:opacity-50"
            >
              {loading.snowflakeVector ? "Searching..." : "Vector Search"}
            </button>
            {errors.snowflakeVector && (
              <div className="rounded-lg bg-red-50 p-4 text-red-800 dark:bg-red-900/20 dark:text-red-200">
                <strong>Error:</strong> {errors.snowflakeVector}
              </div>
            )}
            {snowflakeVectorResult && (
              <div className="rounded-lg bg-indigo-50 p-4 dark:bg-indigo-900/20">
                <div className="flex items-center justify-between mb-2">
                  <p className="font-bold text-indigo-800 dark:text-indigo-200">
                    Search Results:
                  </p>
                  <span className={`px-2 py-1 rounded text-sm font-semibold ${
                    snowflakeVectorResult.success 
                      ? "bg-green-500 text-white" 
                      : "bg-red-500 text-white"
                  }`}>
                    {snowflakeVectorResult.success ? "Success" : "Failed"}
                  </span>
                </div>
                {snowflakeVectorResult.error && (
                  <p className="text-red-600 dark:text-red-300 mb-2">{snowflakeVectorResult.error}</p>
                )}
                {snowflakeVectorResult.results && snowflakeVectorResult.results.length > 0 && (
                  <div className="mt-2 space-y-2 max-h-96 overflow-y-auto">
                    {snowflakeVectorResult.results.map((result, idx) => (
                      <div
                        key={idx}
                        className="rounded-lg bg-white p-3 border border-gray-200 dark:bg-navy-700 dark:border-navy-600"
                      >
                        <pre className="text-xs overflow-x-auto">
                          {JSON.stringify(result, null, 2)}
                        </pre>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
};

export default TestingDashboard;
