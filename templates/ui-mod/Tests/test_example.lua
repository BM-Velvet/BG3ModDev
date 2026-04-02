-- __MOD_NAME__ — Example offline test
-- Run: lua Tests/TestRunner.lua Tests/test_example.lua

local T = require("Tests/TestRunner")

T.describe("Example", function()
    T.it("1 + 1 equals 2", function()
        T.assertEqual(1 + 1, 2)
    end)

    T.it("true is truthy", function()
        T.assertTrue(true)
    end)
end)
