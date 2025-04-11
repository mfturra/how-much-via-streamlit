import pytest
from streamlit.testing.v1 import AppTest
import warnings

# hide streamlit warning to clear up testing output
warnings.filterwarnings("ignore", message=".*missing ScriptRunContext.*")


def test_dataframe_loaded_into_session_state():
    """Ensure that the school data is pre-loaded into session_state.df."""
    at = AppTest.from_file("main.py").run()
    print("\n")

    # Assert the DataFrame exists in session state
    assert "df" in at.session_state, "DataFrame not loaded into session_state"

    # Optionally test that the DataFrame is not empty and has the right columns
    df = at.session_state.df
    assert not df.empty, "Loaded DataFrame is empty"
    assert set(["school name", "school state", "school tuition"]).issubset(df.columns), \
        "Expected columns not found in the DataFrame"

    print("✅ DataFrame successfully loaded into session_state with expected structure.")

@pytest.mark.parametrize("selection", [None, "Amherst College"])
def test_uni_entry(selection):
    """Simulate selecting a university from the selectbox"""
    print("\n")
    at = AppTest.from_file("main.py").run()
    
    # when selection is not None, store cal in school_selection
    if selection is not None:
        at.selectbox[0].select(selection).run()
    
    school_selection = at.selectbox[0].value
    
    if school_selection is None:
        print("✅ Test passed: No selection handled gracefully.")
    else:

        df = at.session_state.df
        expected_tuition = df[df["school name"] == school_selection]["school tuition"].iloc[0]
        expected_output = f"Your estimated tuition costs are: ${expected_tuition:,.2f}"

        # Check if the output was written to the app
        tuition_displayed = any(
            expected_output in element.value for element in at.markdown
        )

        assert tuition_displayed, f"Tuition output not found for {school_selection}"
        print(f"✅ Test passed: Successfully selected '{school_selection}' from the university selectbox and it output {expected_tuition} as the expected tuition.")

