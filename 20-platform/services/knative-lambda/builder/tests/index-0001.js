handle = async (params) => {
    console.log("Link Test " + params.contextId);
    return {"message": "Link Test for index-0001 Worked!" };
  };
module.exports = { handle };