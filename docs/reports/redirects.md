# Redirects and internal links

Every concrete redirect must reach a live page in exactly one hop; wildcard and
placeholder rules have only their target checked. Every root-relative reference in
every built page must resolve; one that resolves only *through* a redirect is
reported as a warning, since Foundation keeps two legacy in-body links verbatim and
the fix belongs in the extractor's rewrite map, not in generated HTML. WordPress
leftovers fail outright; `SITE_URL_PLACEHOLDER` is counted only, as it is expected
until the launch domain is set.

## Problems

None.


## Redirected references (warning)

| page | reference | redirects to |
| --- | --- | --- |
| /buy-blue-staffy-puppies-uk/index.html | /buy-blue-staffy-puppies-for-sale-uk/ | /buy-blue-staffy-puppies-uk/ |
| /buy-staffy-puppies-for-sale-uk/index.html | /category/puppy-buying-guide-uk/ | /blog/ |
| /index.html | /buy-blue-staffy-puppies-for-sale-uk/ | /buy-blue-staffy-puppies-uk/ |
| /uk-blue-staffy-puppy-buying-guide/index.html | /buy-blue-staffy-puppies-for-sale-uk/ | /buy-blue-staffy-puppies-uk/ |
| /uk-blue-staffy-puppy-buying-guide/index.html | /category/puppy-buying-guide-uk/ | /blog/ |
| /uk-locations/blue-staffy-puppies-uk/index.html | /buy-blue-staffy-puppies-for-sale-uk/ | /buy-blue-staffy-puppies-uk/ |

SITE_URL_PLACEHOLDER occurrences: 545 (expected until launch)

examined 18 redirects, 1921 internal refs; 6 redirected refs; 0 problems
