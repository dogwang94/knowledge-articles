/*******************************************************
CREATED BY : DevOps Support
CREATION DATE : 08/07/2023

**** MODIFICATION HISTORY *****
LAST MODIFIED DATE LAST MODIFIED BY DESCRIPTION 
08/07/2023         LW               Initial Draft
 
DESCRIPTION: Function to replace urls 
*********************************************************/

--DROP FUNCTION kabot.func_excluded_user(github_owner text, github_repo text)
CREATE OR REPLACE FUNCTION kabot.func_select_ka(
  github_owner text,
  github_repo text
)
RETURNS SETOF jsonb AS $$
DECLARE
  ka_row record;
  ru_row record;
  content text;
BEGIN
  FOR ka_row IN SELECT * FROM kabot.knowledge_article LOOP
    content := ka_row.content;
    
    FOR ru_row IN SELECT * FROM kabot.resource_url LOOP
      -- Replace {key} with URL
      content := regexp_replace(content,
                                format('{%s}', ru_row.key),
                                ru_row.url,
                                'g');
    END LOOP;
    
    -- Replace GitHub variables
    content := regexp_replace(content,
                              '{GITHUB_REPO_OWNER}',
                              github_owner,
                              'g');
                                
    content := regexp_replace(content,
                              '{GITHUB_KA_REPO_NAME}',
                              github_repo,
                              'g');

    -- Return JSON object with updated content
    RETURN NEXT jsonb_build_object(
        'key', ka_row.key,
        'content', content
    );
  END LOOP;

  RETURN;
END;
$$ LANGUAGE plpgsql;

-- Call it
SELECT *
FROM kabot.func_select_ka('myorg', 'myrepo');

-- Call it
SELECT json_agg(result)
FROM (
  SELECT * 
  FROM kabot.func_select_ka('myorg', 'myrepo') 
) AS result;



--SELECT * FROM pg_proc WHERE proname = 'func_select_ka';