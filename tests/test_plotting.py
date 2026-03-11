from unox import plotting as uplt
from unox import data as udata
from unox.HPC.data0.dataset import uarray
import xarray as xr

# Load the example prediction dataset
pred_u_arr = uarray('no2_example_run', is_predict=True)

def test_BaW_label():
    """Test the BaW_label function."""
    # Define the test cases
    test_cases = [
        {
            'uarray': pred_u_arr,
            'label_with': ['name'],
            'var': 'nox_pred',
            'one_dataset': True,
            'expected_label': 'no2_example_run',
        },
        {
            'uarray': pred_u_arr,
            'label_with': ['name'],
            'var': None,
            'one_dataset': False,
            'expected_label': 'no2_example_run',
        },
        {
            'uarray': pred_u_arr,
            'label_with': ['name', 'size', 'grid_size'],
            'var': 'nox_pred',
            'one_dataset': False,
            'expected_label': 'no2_example_run, n=4892160, [56, 120]',
        },
    ]
    # Test each case
    for case in test_cases:
        actual_label = uplt.BaW_label(
            case['uarray'],
            label_with=case['label_with'],
            var=case['var'],
            one_dataset=case['one_dataset'],
        )
        assert actual_label == case['expected_label'], f"Expected label '{case['expected_label']}', but got '{actual_label}'"
    # Define invalid test cases
    invalid_cases = [
        {
            'uarray': pred_u_arr,
            'label_with': ['size'],
            'var': None,
            'one_dataset': False,
            'expected_label': 'no2_example_run',
        },
        {
            'uarray': pred_u_arr,
            'label_with': ['name'],
            'var': ['R2'],
            'one_dataset': False,
            'expected_label': 'no2_example_run',
        },
        {
            'uarray': pred_u_arr,
            'label_with': ['invalid_label'],
            'var': None,
            'one_dataset': False,
            'expected_label': 'no2_example_run',
        },
    ]
    # Test invalid cases
    for case in invalid_cases:
        try:
            uplt.BaW_label(
                case['uarray'],
                label_with=case['label_with'],
                var=case['var'],
                one_dataset=case['one_dataset'],
            )
            assert False, f"Expected an exception for invalid case with label_with={case['label_with']} and var={case['var']}."
        except Exception:
            pass

def test_select_time():
    """Test the select_time function."""
    # Define xarray objects
    ds_no2_ex = uarray('no2_example_run', is_predict=True).xr
    # Define valid test cases
    test_cases = [
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-02 to 2020-12-31',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': '2019-01-15',
            'end_date': None,
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-15 to 2020-12-31',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': '2019-01-15',
            'end_date': '2019-01-31',
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-15 to 2019-01-31',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': '2019-01-15',
            'end_date': '2019-01-15',
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'on 2019-01-15',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': '2019-01-31',
            'interval': None,
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-02 to 2019-01-31',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '3M',
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-02 to 2019-04-02 (3 M)',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '3D',
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'from 2019-01-02 to 2019-01-05 (3 D)',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '0D',
            'avg_over': False,
            'sum_over': False,
            'expected_title': 'on 2019-01-02 (0 D)',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '3M',
            'avg_over': True,
            'sum_over': False,
            'expected_title': 'Averaged from 2019-01-02 to 2019-04-02 (3 M)',
        },
        {
            'dataset': ds_no2_ex,
            'start_date': None,
            'end_date': None,
            'interval': '3D',
            'avg_over': False,
            'sum_over': True,
            'expected_title': 'Summed from 2019-01-02 to 2019-01-05 (3 D)',
        },
    ]
    # Test each case
    for case in test_cases:
        # Get the actual output
        actual_xr, actual_title = uplt.select_time(
            case['dataset'],
            start_date=case['start_date'],
            end_date=case['end_date'],
            interval=case['interval'],
            avg_over=case['avg_over'],
            sum_over=case['sum_over'],
        )
        # Compare the titles
        assert actual_title == case['expected_title'], f"Expected title '{case['expected_title']}', but got '{actual_title}'"

    # Define invalid dates
    invalid_dates = [
        '2019-02-30',
        '2019-13-01',
        '2019-00-10',
        '2019-01-32',
        'invalid_date',
        123456,
        False,
        [],
        {},
    ]
    # Test invalid dates
    for invalid_date in invalid_dates:
        try:
            uplt.select_time(
                ds_no2_ex,
                start_date=invalid_date,
                end_date=None,
                interval=None,
                avg_over=False,
                sum_over=False,
            )
            assert False, f"Expected an exception for invalid date '{invalid_date}' in `start_date`."
        except Exception:
            pass
        try:
            uplt.select_time(
                ds_no2_ex,
                start_date=None,
                end_date=invalid_date,
                interval=None,
                avg_over=False,
                sum_over=False,
            )
            assert False, f"Expected an exception for invalid date '{invalid_date}' in `start_date`."
        except Exception:
            pass
    # Test when both `avg_over` and `sum_over` are True
    try:
        uplt.select_time(
            ds_no2_ex,
            start_date=None,
            end_date=None,
            interval=None,
            avg_over=True,
            sum_over=True,
        )
        assert False, "Expected an exception when both `avg_over` and `sum_over` are True."
    except Exception:
        pass