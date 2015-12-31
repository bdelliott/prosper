import api


def _equal(x, y, allowed_error=0.0001):
    return abs(x - y) <= allowed_error


def check_sanity(prosper):
    """Check that total account value actually adds up given all transactions
    
    It should equal:
      cash + 
      pending investments (primary market) +
      pending investments (secondary market) +
      (total in active notes -
      total principal received on active notes) - 
      pending quick invest orders

    """

    ## test the account level view of things:
    account = prosper.account()

    total = account['total_account_value']

    cash = account['available_cash_balance']
    pending = (account['pending_investments_primary_market'] +
               account['pending_investments_secondary_market'])

    # check that principal received/outstanding matches total in active notes:
    active = account['total_amount_invested_on_active_notes']
    principal_outstanding = account['outstanding_principal_on_active_notes']
    principal_received = account['total_principal_received_on_active_notes']
    assert active == (principal_outstanding + principal_received)

    pending_quick = account['pending_quick_invest_orders']

    calc_total = cash + pending + principal_outstanding - pending_quick

    if not _equal(total, calc_total):
        raise Exception("Stated total $%0.2f doesn't equal calculated total "
                        "$%0.2f" % (total, calc_total))

    ## ok now sum up active notes as another layer of sanity checking:
    notes = prosper.notes()

    p_outstanding = 0.0
    p_owned = 0.0
    p_service_fees = 0.0

    for note in notes:
        print note
        print "-"*80

        p_outstanding += note['principal_balance_pro_rata_share']
        p_service_fees = note['service_fees_paid_pro_rata_share']
        p_owned += note['note_ownership_amount']
        
    import pdb; pdb.set_trace()

    

if __name__ == '__main__':
    prosper = api.Prosper()
    # sanity check that the api view of the account values is at least
    # consistent:
    check_sanity(prosper)
