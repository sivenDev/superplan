# Bug Diagnosis

Read this reference before planning an accepted bug whose cause is not already
demonstrated by current evidence. Diagnosis does not authorize a fix.

1. Reproduce the failure with the narrowest reliable command or observation. If
   reproduction is unavailable, record stable evidence and what remains unknown.
2. Inspect the failing path, recent relevant changes, configuration, inputs, and
   a working analogue only as needed.
3. State one falsifiable root-cause hypothesis and run the cheapest check that
   distinguishes it from plausible alternatives.
4. Trace invalid values or side effects back to their first incorrect source;
   avoid patching only the final symptom or adding duplicate guards without a
   distinct risk boundary.
5. Keep the bugfix plan's `Reproduction` and `Root Cause` tied to observed
   evidence. Stay in diagnosis when the cause cannot yet be explained.

During approved implementation, capture a focused failing behavior regression
before the fix when practical and trustworthy, apply the smallest source-level
change, and rerun the reproduction plus proportionate regression checks. For
asynchronous flakiness, wait on the observable condition with a finite timeout
instead of adding guessed sleeps. Remove temporary instrumentation and avoid
unrelated cleanup.
