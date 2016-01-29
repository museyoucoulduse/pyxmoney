class _helpers:
    ''' Helper functions '''
    def _correct_pips(sl_or_tp, instrument, instlst, pipslst):
        pip = pipslst[instlst.index(instrument)]
        # print(pip)
        if float(pip) == 1.0:
            return sl_or_tp / 10
        elif float(pip) == 0.01:
            return sl_or_tp / 1000
        else:
            return sl_or_tp / 100000

    def _step_and_max_sltp(granularity):
        if granularity in [
            'S5',
            'S10',
            'S15',
        ]:
            return 20, 280, 240
        elif granularity in [
            'S30',
            'M1',
            'M2',
            'M3',
            'M4',
            'M5',
        ]:
            return 50, 650, 700
        elif granularity in [
            'M10',
            'M15',
            'M30',
        ]:
            return 100, 1200, 1500
        else:
            return 200, 2800, 3000

    def _getGranularitySeconds(granularity):
        if granularity[0] == 'S':
            return int(granularity[1:])
        elif granularity[0] == 'M' and len(granularity) > 1:
            return 60*int(granularity[1:])
        elif granularity[0] == 'H':
            return 60*60*int(granularity[1:])
        elif granularity[0] == 'D':
            return 60*60*24
        elif granularity[0] == 'W':
            return 60*60*24*7
            #Does not take into account actual month length
        elif granularity[0] == 'M':
            return 60*60*24*30
