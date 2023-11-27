/*******************************************************
CREATED BY : DevOps Support
CREATION DATE : 09/29/2023

**** MODIFICATION HISTORY *****
LAST MODIFIED DATE LAST MODIFIED BY DESCRIPTION 
09/29/2023         LW               Initial Draft
10/25/2023         LW               Rewrite
DESCRIPTION: Function to check user exluded 
RETURN: boolan is_excluded
*********************************************************/

--DROP FUNCTION kabot.func_excluded_user(new_user_email)
CREATE OR REPLACE FUNCTION kabot.func_excluded_user(new_user_email VARCHAR)
RETURNS BOOLEAN AS $$
DECLARE
    is_excluded BOOLEAN;
BEGIN
    -- Check if the new_user_email exists in devops_user table
    is_excluded := EXISTS (SELECT 1 FROM kabot.devops_user WHERE "email" = new_user_email);
    
    -- Return true if the email address is excluded, otherwise return false
    RETURN NOT is_excluded;
END;
$$ LANGUAGE plpgsql;

-- Test the func_excluded_user function with a specific email address
SELECT kabot.func_excluded_user('liping.wang2@va.gov') AS is_excluded;